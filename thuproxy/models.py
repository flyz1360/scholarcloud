from django.db import models
from django.contrib.auth.models import User


# class DUser(models.Model):
#     user = models.OneToOneField(User)


class ProxyAccount(models.Model):
    user = models.ForeignKey(User)
    type = models.IntegerField()
    paydate = models.DateField(blank=True, null=True)
    expired_date = models.DateField(blank=True, null=True)
    port = models.IntegerField()
    traffic = models.FloatField()
    pac_no = models.CharField(blank=True, null=True, max_length=255)

class Pay(models.Model):
    out_trade_no = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    status = models.CharField(max_length=2)
    total_fee = models.FloatField()
    type = models.IntegerField()
    month = models.IntegerField()
    buy_id = models.CharField(max_length=255)
    buy_email = models.CharField(max_length=255)
    create_date = models.DateField(blank=True, null=True)