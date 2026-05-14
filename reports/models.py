from django.db import models
from django.utils import timezone


class MonthlyNewsletter(models.Model):
    month = models.IntegerField()
    year = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('month', 'year')

    def __str__(self):
        return f"Newsletter {self.month}/{self.year}"


class MonthlyReport(models.Model):
    month = models.IntegerField()
    year = models.IntegerField()
    data_snapshot = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('month', 'year')
        ordering = ['-year', '-month']

    def __str__(self):
        return f"Report {self.month}/{self.year}"
