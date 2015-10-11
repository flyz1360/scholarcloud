from django.db import models
from django.contrib.auth.models import User


class DUser(models.Model):
    user = models.OneToOneField(User)

class ProxyAccount(models.Model):
    type = models.IntegerField()
    paydate = models.DateField(blank=True, null=True)
    month = models.IntegerField()
    port = models.IntegerField()
