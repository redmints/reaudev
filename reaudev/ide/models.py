from django.db import models

# Create your models here.

class User(models.Model):
    username = models.fields.CharField(max_length=100)
    email = models.fields.CharField(max_length=100)
    password = models.fields.CharField(max_length=100)
    type = models.fields.IntegerField()

class Project(models.Model):
    name = models.fields.CharField(max_length=100)
    type = models.fields.IntegerField()
    status = models.fields.IntegerField()

class User_Project(models.Model):
    id_user = models.fields.IntegerField()
    id_project = models.fields.IntegerField()
    role = models.fields.IntegerField()