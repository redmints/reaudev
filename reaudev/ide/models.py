from django.db import models

# Create your models here.

class User(models.Model):
    username = models.fields.CharField(max_length=100)
    email = models.fields.CharField(max_length=100)
    password = models.fields.CharField(max_length=100)
    type = models.fields.IntegerField()

    def _get_role(self, project):
        up = User_Project.objects.filter(user=self, project=project)
        if len(up) > 0:
            return up[0].role
        else:
            return None

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

class Group(models.Model):
    name = models.fields.CharField(max_length=100)

class User_Group(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, default=1)
