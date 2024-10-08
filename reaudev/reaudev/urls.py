"""
URL configuration for reaudev project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ide import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('signup/', views.signup),
    path('login/', views.login),
    path('create-project/', views.create_project),
    path('editor/', views.editor),
    path('cat/', views.cat),
    path('ls/', views.ls),
    path('touch/', views.touch),
    path('writefile/', views.write_file),
    path('project-settings/', views.project_settings),
    path('search-user/', views.search_user),
    path('search-group/', views.search_group),
    path('change-user/', views.change_user),
    path('rm/', views.rm),
    path('delete-project/', views.delete_project),
]
