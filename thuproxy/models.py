from django.db import models
from django.contrib.auth.models import User


class DUser(models.Model):
    user = models.OneToOneField(User)


class ProxyAccount(models.Model):
    user = models.ForeignKey(User)
    type = models.IntegerField()
    paydate = models.DateField(blank=True, null=True)
    expired_date = models.DateField(blank=True, null=True)
    port = models.IntegerField()
    traffic = models.FloatField()
