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

    def _get_owner(self):
        for up in User_Project.objects.filter(project=self):
            if up.role == 1:
                return up.user
    owner = property(_get_owner)

class User_Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=1)
    role = models.fields.IntegerField()