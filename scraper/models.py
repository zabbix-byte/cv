from django.db import models
from django.contrib.auth.models import User


class UserProfileHtml(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    data = models.JSONField()
    last_modified = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)
