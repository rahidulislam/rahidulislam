from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models.deletion import ProtectedError
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.analytics.selectors import traffic_report
from apps.articles.rendering import render_article
from apps.contacts.models import Contact
from apps.contacts.services import retry_enquiry_notification, update_enquiry_status

from .auth import owner_required
from .forms import AnalyticsFilterForm, EnquiryActionForm, OwnerAuthenticationForm
from .resources import RESOURCE_MAP
from .selectors import (
    content_by_pk,
    content_list,
    deletion_summary,
    enquiry_by_pk,
    enquiry_list,
    first_content,
    navigation,
    overview,
    table_rows,
)


class OwnerLoginView(LoginView):
    template_name = "dashboard/login.html"
    authentication_form = OwnerAuthenticationForm
    next_page = reverse_lazy("dashboard:overview")


class OwnerLogoutView(LogoutView):
    next_page = reverse_lazy("dashboard:login")


def context(**kwargs) -> dict:
    return {"nav_groups": navigation(), **kwargs}


def resource_get(key):
    try:
        return RESOURCE_MAP[key]
    except KeyError as exc:
        raise Http404 from exc


@owner_required
@require_GET
def index(request):
    today = timezone.localdate()
    report = traffic_report(start=today, end=today)
    return render(
        request,
        "dashboard/overview.html",
        context(title="Overview", active="overview", report=report, **overview()),
    )


@owner_required
@require_GET
def analytics(request):
    form = AnalyticsFilterForm(request.GET or {"period": "30"})
    report = None
    if form.is_valid():
        report = traffic_report(
            start=form.cleaned_data["start"], end=form.cleaned_data["end"]
        )
    return render(
        request,
        "dashboard/analytics.html",
        context(
            title="Visitor analytics", active="analytics", form=form, report=report
        ),
    )


@owner_required
@require_GET
def listing(request, resource):
    resource = resource_get(resource)
    query = request.GET.get("q", "")[:200]
    parent = request.GET.get(resource.parent, "") if resource.parent else ""
    items = content_list(resource=resource, query=query, parent=parent)
    page = Paginator(items, 20).get_page(request.GET.get("page"))
    headers = [
        resource.model._meta.get_field(name).verbose_name for name in resource.columns
    ]
    return render(
        request,
        "dashboard/list.html",
        context(
            title=resource.label,
            active=resource.key,
            resource=resource,
            page=page,
            rows=table_rows(resource=resource, objects=page),
            headers=headers,
            query=query,
            parent=parent,
            can_add=not (
                resource.singleton and first_content(resource=resource) is not None
            ),
        ),
    )


@owner_required
@require_http_methods(["GET", "POST"])
def editor(request, resource, pk=None):
    resource = resource_get(resource)
    obj = content_by_pk(resource=resource, pk=pk) if pk is not None else None
    if pk is not None and obj is None:
        raise Http404
    if obj is None and resource.singleton:
        existing = first_content(resource=resource)
        if existing:
            return redirect("dashboard:edit", resource=resource.key, pk=existing.pk)
    initial = {}
    if resource.parent:
        parent = request.GET.get(resource.parent, "")
        if parent.isdecimal() and len(parent) <= 18:
            initial[resource.parent] = parent
    form = resource.form_class()(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
        instance=obj,
        initial=initial,
    )
    if request.method == "POST" and form.is_valid():
        try:
            saved = resource.save(
                obj=form.save(commit=False),
                actor=request.user,
                changed_fields=form.changed_data,
            )
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(
                request, f"{resource.model._meta.verbose_name.capitalize()} saved."
            )
            return redirect("dashboard:edit", resource=resource.key, pk=saved.pk)
    related = []
    if obj and resource.key in {"projects", "experiences"}:
        related = [
            item
            for item in RESOURCE_MAP.values()
            if item.parent
            == ("project" if resource.key == "projects" else "experience")
        ]
    return render(
        request,
        "dashboard/editor.html",
        context(
            title=f"{'Edit' if obj else 'Add'} {resource.model._meta.verbose_name}",
            active=resource.key,
            resource=resource,
            obj=obj,
            form=form,
            related=related,
        ),
    )


@owner_required
@require_http_methods(["GET", "POST"])
def delete(request, resource, pk):
    resource = resource_get(resource)
    if not resource.deletable:
        raise Http404
    obj = content_by_pk(resource=resource, pk=pk)
    if obj is None:
        raise Http404
    error = ""
    if request.method == "POST":
        try:
            resource.delete(obj=obj, actor=request.user)
        except (ValidationError, ProtectedError):
            error = (
                "This record could not be deleted because related data must be kept."
            )
        else:
            messages.success(request, "Record deleted.")
            return redirect("dashboard:list", resource=resource.key)
    return render(
        request,
        "dashboard/delete.html",
        context(
            title="Confirm deletion",
            active=resource.key,
            resource=resource,
            obj=obj,
            summary=deletion_summary(obj),
            error=error,
        ),
    )


@owner_required
@require_POST
def preview(request):
    return HttpResponse(
        render_article(request.POST.get("body", "")[:200000]), content_type="text/html"
    )


@owner_required
@require_GET
def inbox(request):
    query, status = request.GET.get("q", "")[:200], request.GET.get("status", "")
    page = Paginator(enquiry_list(query=query, status=status), 20).get_page(
        request.GET.get("page")
    )
    return render(
        request,
        "dashboard/inbox.html",
        context(
            title="Inbox",
            active="inbox",
            query=query,
            status=status,
            statuses=Contact.STATUS_CHOICES,
            page=page,
        ),
    )


@owner_required
@require_http_methods(["GET", "POST"])
def enquiry(request, pk):
    item = enquiry_by_pk(pk=pk)
    if item is None:
        raise Http404
    form = EnquiryActionForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        action = form.cleaned_data["action"]
        if action == "retry":
            try:
                result = retry_enquiry_notification(enquiry=item, actor=request.user)
            except ValueError as exc:
                form.add_error(None, str(exc))
            else:
                if result == "sent":
                    messages.success(request, "Notification sent.")
                else:
                    messages.error(
                        request,
                        "Notification delivery failed. The message remains saved; you can retry later.",
                    )
                return redirect("dashboard:enquiry", pk=pk)
        else:
            update_enquiry_status(enquiry=item, status=action, actor=request.user)
            messages.success(request, f"Message marked {action}.")
            return redirect("dashboard:enquiry", pk=pk)
    return render(
        request,
        "dashboard/enquiry.html",
        context(title=item.subject, active="inbox", item=item, form=form),
    )


@owner_required
@require_GET
def cv_preview(request):
    from io import BytesIO

    from django.http import FileResponse

    from apps.resumes.services import generate_cv

    return FileResponse(
        BytesIO(generate_cv()),
        content_type="application/pdf",
        filename="Rahidul_Islam_CV.pdf",
    )
