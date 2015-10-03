from django.db import models


class User(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=40)
    email = models.EmailField()
    # proxy = models.OneToOneField('ProxyAccount')


class ProxyAccount(models.Model):
    username = models.CharField(max_length=30)
    type = models.IntegerField()
    month = models.IntegerField()
    port = models.IntegerField()
