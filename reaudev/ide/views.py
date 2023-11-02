from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from ide.models import User
from ide.models import Project
from ide.models import User_Project
from ide.utils import *
from django.conf import settings
import base64
import hashlib
import json
import shutil
import os

# Create your views here.

def home(request):
    if request.session.get('id_user'):
        user = User.objects.filter(id=request.session.get('id_user'))[0]
        projects = User_Project.objects.filter(user=user)
        return render(request, 'ide/home.html', {'user': user, 'projects': projects})
    else:
        return redirect("/login")
    
def cat(request):
    user = User.objects.filter(id=request.session.get('id_user'))[0]
    project = Project.objects.filter(id=request.GET['id_project'])[0]
    cmd = '/home/'+str(request.session.get('id_user'))+'/'+str(request.GET['id_project'])+'/'+str(request.GET['file'])
    if "id_user" in request.GET:
        if user._get_role(project) in [1, 3]:
            cmd = '/home/'+str(request.GET['id_user'])+'/'+str(request.GET['id_project'])+'/'+str(request.GET['file'])
    content = str(docker_cat(cmd)[1], "utf-8")
    return HttpResponse(content)

def rm(request):
    user = User.objects.filter(id=request.session.get('id_user'))[0]
    project = Project.objects.filter(id=request.GET['id_project'])[0]
    cmd = settings.SHARED_DIRECTORY+str(request.session.get('id_user'))+'/'+str(request.GET['id_project'])+'/'+str(request.GET['filename'])
    if "id_user" in request.GET:
        if user._get_role(project) == 1:
            cmd = settings.SHARED_DIRECTORY+str(request.GET['id_user'])+'/'+str(request.GET['id_project'])+'/'+str(request.GET['filename'])
    os.remove(cmd)
    return HttpResponse("OK")

def ls(request):
    user = User.objects.filter(id=request.session.get('id_user'))[0]
    project = Project.objects.filter(id=request.GET['id_project'])[0]
    cmd = '/home/'+str(request.session.get('id_user'))+'/'+str(request.GET['id_project'])
    if "id_user" in request.GET:
        if user._get_role(project) in [1, 3]:
            cmd = '/home/'+str(request.GET['id_user'])+'/'+str(request.GET['id_project'])
    content = str(docker_ls(cmd)[1], "utf-8")
    return HttpResponse(content)

def touch(request):
    user = User.objects.filter(id=request.session.get('id_user'))[0]
    project = Project.objects.filter(id=request.GET['id_project'])[0]
    cmd = settings.SHARED_DIRECTORY+str(request.session.get('id_user'))+'/'+str(request.GET['id_project'])+'/'+str(request.GET['filename'])
    if "id_user" in request.GET:
        if user._get_role(project) == 1:
            cmd = settings.SHARED_DIRECTORY+str(request.GET['id_user'])+'/'+str(request.GET['id_project'])+'/'+str(request.GET['filename'])
    docker_touch(cmd)
    return HttpResponse("OK")

def write_file(request):
    if request.method == "POST":
        json_data = json.loads(request.body)
        user = User.objects.filter(id=request.session.get('id_user'))[0]
        project = Project.objects.filter(id=json_data['id_project'])[0]
        cmd = settings.SHARED_DIRECTORY+str(request.session.get('id_user'))+'/'+str(json_data['id_project'])+'/'+str(json_data['filename'])
        if "id_user" in json_data:
            if user._get_role(project) == 1:
                cmd = settings.SHARED_DIRECTORY+str(json_data['id_user'])+'/'+str(json_data['id_project'])+'/'+str(json_data['filename'])
        docker_write_file(cmd, json_data['content'])
    return HttpResponse("OK")

def search_user(request):
    if 'q' in request.GET and len(request.GET['q']) >= 2:
        id_in_project = User_Project.objects.filter(project__id=request.GET['id_project']).values('user__id')
        users = User.objects.filter(username__icontains=request.GET['q']).exclude(id__in=id_in_project) | User.objects.filter(email__icontains=request.GET['q']).exclude(id__in=id_in_project)
        tab = []
        for user in users:
            dict = {}
            dict['id'] = user.id
            dict['text'] = user.username+' ('+user.email+')'
            tab.append(dict)
        return HttpResponse(json.dumps(tab))
    return HttpResponse("OK")

def project_settings(request):
    if request.session.get('id_user'):
        user = User.objects.filter(id=request.session.get('id_user'))[0]
        project = Project.objects.filter(id=request.GET['id'])[0]
        if user._get_role(project) == 1:
            if request.method == "POST":
                if request.POST['user_id']:
                    if not User_Project.objects.filter(user__id=request.POST['user_id'], project__id=request.GET['id']):
                        up = User_Project()
                        up.project = project
                        up.user = User.objects.filter(id=request.POST['user_id'])[0]
                        up.role = request.POST['user_role']
                        up.save()
                        docker_create_project(up.user.id, project.id)
            users = User_Project.objects.filter(project=project)
            return render(request, 'ide/project-settings.html', {'user': user, 'project': project, 'users': users, 'reau_url': settings.REAUDEV_URL})
    return redirect("/login")

def change_user(request):
    if request.session.get('id_user'):
        if User.objects.filter(id=request.session.get('id_user'))[0]._get_role(Project.objects.filter(id=request.GET["id_project"])[0]) == 1:
            if request.GET['action'] == "change":
                User_Project.objects.filter(user__id=request.GET["id_user"], project__id=request.GET["id_project"]).update(role=request.GET['role'])
            if request.GET['action'] == "delete":
                User_Project.objects.filter(user__id=request.GET["id_user"], project__id=request.GET["id_project"]).delete()
                shutil.rmtree(settings.SHARED_DIRECTORY+str(request.GET["id_user"])+"/"+str(request.GET["id_project"]))
                return redirect("/project-settings/?id="+request.GET["id_project"])
    return HttpResponse("OK")
    
def editor(request):
    if request.session.get('id_user') and request.method == "GET":
        user = User.objects.filter(id=request.session.get('id_user'))[0]
        project = Project.objects.filter(id=request.GET['id_project'])[0]
        up = None
        user_to_see = None
        if user._get_role(project):
            files = str(docker_ls('/home/'+str(request.session.get('id_user'))+'/'+str(project.id))[1], "utf-8").split('\n')
            if user._get_role(project) == 1:
                up = User_Project.objects.filter(project=project, role__in=[2, 3])
            if "id_user" in request.GET:
                if user._get_role(project) in [1, 4]:
                    user_to_see = User.objects.filter(id=request.GET['id_user'])[0]
                if user._get_role(project) == 3:
                    user_to_see = project.owner
                files = str(docker_ls('/home/'+str(user_to_see.id)+'/'+str(project.id))[1], "utf-8").split('\n')
            user.password_b64 = str(base64.b64encode(user.password.encode('ascii')), "utf-8")
            files.pop(len(files)-1)
            return render(request, 'ide/editor.html', {'user': user, 'project': project, 'files': files, 'role': user._get_role(project), 'users': up, 'user_to_see': user_to_see, 'reau_url': settings.REAUDEV_URL})
    return redirect("/login")
    
def create_project(request):
    if request.session.get('id_user') and request.method == "POST":
        project = Project()
        project.name = request.POST['name']
        project.type = 1
        project.status = 1
        project.save()
        user_project = User_Project()
        user_project.user = User.objects.filter(id=request.session.get('id_user'))[0]
        user_project.project = project
        user_project.role = 1
        user_project.save()
        docker_create_project(request.session.get('id_user'), project.id)
    return redirect("/")

def delete_project(request):
    if request.session.get('id_user') and request.method == "GET":
        user = User.objects.filter(id=request.session.get('id_user'))[0]
        project = Project.objects.filter(id=request.GET['id_project'])[0]
        if user._get_role(project) == 1:
            shutil.rmtree(settings.SHARED_DIRECTORY+str(user.id)+"/"+str(project.id))
            project.delete()
        return redirect("/")

def signup(request):
    if request.method == "POST":
        user = User()
        form = request.POST
        if not User.objects.filter(email=form['email']):
            user.username = form['name']
            user.email = form['email']
            user.password = hashlib.sha256(form['password'].encode('utf-8')).hexdigest()
            user.type = 0
            user.save()
            print(docker_create_user(user.id, user.password))
            return redirect("/login")
        else:
            return redirect("/signup")
    else:
        return render(request, 'ide/signup.html')
    
def login(request):
    if request.session.get('id_user'):
        del request.session['id_user']
    if request.method == "POST":
        form = request.POST
        user = User.objects.filter(email=form['email'])[0]
        if not user:
            return redirect("/signup")
        if user.password == hashlib.sha256(form['password'].encode('utf-8')).hexdigest():
            request.session['id_user'] = user.id
            return redirect("/")
        else:
            return redirect("/login")
    else:
        return render(request, 'ide/login.html')