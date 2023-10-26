from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from ide.models import User
from ide.models import Project
from ide.models import User_Project
from ide.utils import *
import base64
import hashlib
import json
import shutil

# Create your views here.

def home(request):
    if request.session.get('id_user'):
        user = User.objects.filter(id=request.session.get('id_user'))[0]
        projects = User_Project.objects.filter(user=user)
        return render(request, 'ide/home.html', {'user': user, 'projects': projects})
    else:
        return redirect("/login")
    
def cat(request):
    content = str(docker_cat('/home/'+str(request.session.get('id_user'))+'/'+str(request.GET['id_project'])+'/'+str(request.GET['file']))[1], "utf-8")
    return HttpResponse(content)

def rm(request):
    docker_rm('/tmp/reaudev/'+str(request.session.get('id_user'))+'/'+str(request.GET['id_project'])+'/'+str(request.GET['filename']))
    return HttpResponse("OK")

def ls(request):
    content = str(docker_ls('/home/'+str(request.session.get('id_user'))+'/'+str(request.GET['id_project']))[1], "utf-8")
    return HttpResponse(content)

def touch(request):
    docker_touch('/tmp/reaudev/'+str(request.session.get('id_user'))+'/'+str(request.GET['id_project'])+'/'+str(request.GET['filename']))
    return HttpResponse("OK")

def write_file(request):
    if request.method == "POST":
        json_data = json.loads(request.body)
        docker_write_file('/tmp/reaudev/'+str(request.session.get('id_user'))+'/'+str(json_data['id_project'])+'/'+str(json_data['filename']), json_data['content'])
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
            return render(request, 'ide/project-settings.html', {'user': user, 'project': project, 'users': users})
    return redirect("/login")

def change_user(request):
    if request.session.get('id_user'):
        if User.objects.filter(id=request.session.get('id_user'))[0]._get_role(Project.objects.filter(id=request.GET["id_project"])[0]) == 1:
            if request.GET['action'] == "change":
                User_Project.objects.filter(user__id=request.GET["id_user"], project__id=request.GET["id_project"]).update(role=request.GET['role'])
            if request.GET['action'] == "delete":
                User_Project.objects.filter(user__id=request.GET["id_user"], project__id=request.GET["id_project"]).delete()
                shutil.rmtree("/tmp/reaudev/"+str(request.GET["id_user"])+"/"+str(request.GET["id_project"]))
                return redirect("/project-settings/?id="+request.GET["id_project"])
    return HttpResponse("OK")
    
def editor(request):
    if request.session.get('id_user') and request.method == "GET":
        user = User.objects.filter(id=request.session.get('id_user'))[0]
        project = Project.objects.filter(id=request.GET['id'])[0]
        up = None
        if user._get_role(project):
            if user._get_role(project) == 1:
                up = User_Project.objects.filter(project=project, role__in=[2, 3])
            user.password_b64 = str(base64.b64encode(user.password.encode('ascii')), "utf-8")
            files = str(docker_ls('/home/'+str(request.session.get('id_user'))+'/'+str(project.id))[1], "utf-8").split('\n')
            files.pop(len(files)-1)
            return render(request, 'ide/editor.html', {'user': user, 'project': project, 'files': files, 'role': user._get_role(project), 'users': up})
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
            shutil.rmtree("/tmp/reaudev/"+str(user.id)+"/"+str(project.id))
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