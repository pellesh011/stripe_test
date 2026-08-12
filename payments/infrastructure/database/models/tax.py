from django.db import models


class TaxModel(models.Model):
    name = models.CharField(max_length=255)
    rate = models.IntegerField()
