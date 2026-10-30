"""Cookie-free details expire; daily aggregates contain no visitor identifiers."""

from django.db import models


class DailyTraffic(models.Model):
    date = models.DateField(unique=True)
    views = models.PositiveIntegerField(default=0)
    visitors = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["date"]


class DailyVisitor(models.Model):
    date = models.DateField(db_index=True)
    key = models.CharField(max_length=64)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "key"], name="unique_daily_visitor")
        ]


class PageView(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    path = models.CharField(max_length=500)
    referrer = models.CharField(max_length=253, blank=True)


class DailyPage(models.Model):
    date = models.DateField()
    path = models.CharField(max_length=500)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "path"], name="unique_daily_page")
        ]


class DailyReferrer(models.Model):
    date = models.DateField()
    domain = models.CharField(max_length=253, blank=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["date", "domain"], name="unique_daily_referrer"
            )
        ]
