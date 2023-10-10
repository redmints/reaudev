from django.contrib import admin
from ide.models import User
from ide.models import Project
from ide.models import User_Project

# Register your models here.

admin.site.register(User)
admin.site.register(Project)
admin.site.register(User_Project)