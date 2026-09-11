from django.db import models


class VisitSession(models.Model):
    sid = models.CharField(max_length=64, unique=True, db_index=True)
    ip = models.GenericIPAddressField()
    country = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=80, blank=True)
    region = models.CharField(max_length=80, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_seen"]

    def __str__(self):
        place = ", ".join(p for p in (self.city, self.country) if p) or "Unknown"
        return f"{self.ip} · {place}"


class PageView(models.Model):
    session = models.ForeignKey(
        VisitSession, on_delete=models.CASCADE, related_name="views"
    )
    path = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=255, blank=True)
    referrer = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    seconds = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.path} ({self.seconds}s)"
