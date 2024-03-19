from django.db import models


# Create your models here.


class User(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=10)
    phoneNumber = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    userId = models.AutoField(primary_key=True)
