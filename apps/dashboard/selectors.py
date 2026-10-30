"""Read queries and presentation rows, without persistence or HTTP handling."""

from functools import reduce
from operator import or_

from django.contrib.admin.models import LogEntry
from django.contrib.admin.utils import NestedObjects
from django.db.models import Model, Q, QuerySet

from apps.articles.models import Article
from apps.contacts.models import Contact
from apps.projects.models import Project

from .resources import RESOURCES, Resource


def navigation() -> list[dict]:
    groups = []
    for label in dict.fromkeys(resource.group for resource in RESOURCES):
        groups.append(
            {
                "label": label,
                "items": [
                    resource for resource in RESOURCES if resource.group == label
                ],
            }
        )
    return groups


def content_list(*, resource: Resource, query: str, parent: str = "") -> QuerySet:
    items = resource.model.objects.all()
    relations = [
        field.name for field in resource.model._meta.fields if field.many_to_one
    ]
    if relations:
        items = items.select_related(*relations)
    if query and resource.search:
        items = items.filter(
            reduce(
                or_, [Q(**{f"{field}__icontains": query}) for field in resource.search]
            )
        )
    if resource.parent and parent:
        if not parent.isdecimal() or len(parent) > 18:
            return items.none()
        items = items.filter(**{resource.parent + "_id": parent})
    if not items.ordered:
        items = items.order_by("-pk")
    return items


def table_rows(*, resource: Resource, objects) -> list[dict]:
    return [
        {
            "object": obj,
            "cells": [display_value(obj, name) for name in resource.columns],
        }
        for obj in objects
    ]


def display_value(obj, name: str) -> str:
    value = getattr(obj, name)
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if value is None or value == "":
        return "—"
    return str(value)


def overview() -> dict:
    return {
        "unread": Contact.objects.filter(status="unread").count(),
        "published_projects": Project.objects.filter(is_published=True).count(),
        "published_articles": Article.objects.filter(is_published=True).count(),
        "recent_enquiries": Contact.objects.all()[:5],
        "recent_changes": LogEntry.objects.select_related("user").order_by(
            "-action_time"
        )[:8],
    }


def enquiry_list(*, query: str, status: str) -> QuerySet[Contact]:
    items = Contact.objects.all()
    if query:
        items = items.filter(
            Q(name__icontains=query)
            | Q(email__icontains=query)
            | Q(subject__icontains=query)
            | Q(message__icontains=query)
        )
    if status in dict(Contact.STATUS_CHOICES):
        items = items.filter(status=status)
    return items


def deletion_summary(obj) -> list[dict]:
    collector = NestedObjects(using=obj._state.db or "default")
    collector.collect([obj])
    return [
        {"label": model._meta.verbose_name_plural, "count": len(objects)}
        for model, objects in collector.data.items()
    ]


def first_content(*, resource: Resource) -> Model | None:
    return resource.model.objects.order_by("pk").first()


def content_by_pk(*, resource: Resource, pk: int) -> Model | None:
    return resource.model.objects.filter(pk=pk).first()


def enquiry_by_pk(*, pk: int) -> Contact | None:
    return Contact.objects.filter(pk=pk).first()
