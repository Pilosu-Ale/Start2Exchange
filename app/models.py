from django.db import models
from djongo.models.fields import ObjectIdField, Field
from django.contrib.auth.models import User


class Profile(models.Model):
    _id = ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ips = models.Field(default=[])
    subprofiles = models.Field(default={})
    BTC_wallet = models.FloatField(default=0.0)
    balance = models.FloatField(default=0.0)


class Order(models.Model):
    _id = ObjectIdField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    quantity = models.FloatField()
    status = models.Field(default="")
    position = models.Field(default="")