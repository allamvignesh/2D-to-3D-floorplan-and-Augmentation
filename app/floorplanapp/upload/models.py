from django.db import models


class Document(models.Model):
    docfile = models.FileField(upload_to='static/%Y_%m_%d')

class HouseModel(models.Model):
    docfile = models.FileField(upload_to='static/%Y_%m_%d')