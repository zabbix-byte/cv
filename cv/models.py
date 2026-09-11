from django.db import models


class VisitSession(models.Model):
    sid = models.CharField(max_length=64, unique=True, db_index=True)
    ip = models.GenericIPAddressField()
    country = models.CharField(max_length=80, blank=True)
    country_code = models.CharField(max_length=8, blank=True)
    continent = models.CharField(max_length=40, blank=True)
    city = models.CharField(max_length=80, blank=True)
    region = models.CharField(max_length=80, blank=True)
    postal = models.CharField(max_length=20, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    isp = models.CharField(max_length=120, blank=True)
    org = models.CharField(max_length=120, blank=True)
    timezone_ip = models.CharField(max_length=64, blank=True)
    connection_type = models.CharField(max_length=40, blank=True)
    user_agent = models.TextField(blank=True)
    browser = models.CharField(max_length=40, blank=True)
    os = models.CharField(max_length=40, blank=True)
    device = models.CharField(max_length=40, blank=True)
    language = models.CharField(max_length=40, blank=True)
    timezone_client = models.CharField(max_length=64, blank=True)
    screen = models.CharField(max_length=24, blank=True)
    viewport = models.CharField(max_length=24, blank=True)
    pixel_ratio = models.FloatField(null=True, blank=True)
    cores = models.PositiveSmallIntegerField(null=True, blank=True)
    memory_gb = models.FloatField(null=True, blank=True)
    connection_effective = models.CharField(max_length=20, blank=True)
    downlink = models.FloatField(null=True, blank=True)
    touch = models.BooleanField(null=True, blank=True)
    color_scheme = models.CharField(max_length=12, blank=True)
    platform = models.CharField(max_length=80, blank=True)
    landing_path = models.CharField(max_length=255, blank=True)
    referrer = models.TextField(blank=True)
    utm_source = models.CharField(max_length=80, blank=True)
    utm_medium = models.CharField(max_length=80, blank=True)
    utm_campaign = models.CharField(max_length=80, blank=True)
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
