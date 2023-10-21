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

# Create your views here.

def home(request):
    if request.session.get('id_user'):
        user = User.objects.filter(id=request.session.get('id_user'))[0]
        projects = get_projects(user.id)
        return render(request, 'ide/home.html', {'user': user, 'projects': projects})
    else:
        return redirect("/login")
    
def cat(request):
    content = str(docker_cat('/home/'+str(request.session.get('id_user'))+'/'+str(request.GET['id_project'])+'/'+str(request.GET['file']))[1], "utf-8")
    return HttpResponse(content)

def ls(request):
    content = str(docker_ls('/home/'+str(request.session.get('id_user'))+'/'+str(request.GET['id_project']))[1], "utf-8")
    return HttpResponse(content)

def touch(request):
    content = str(docker_touch('/tmp/reaudev/'+str(request.session.get('id_user'))+'/'+str(request.GET['id_project'])+'/'+str(request.GET['filename']))[1], "utf-8")
    return HttpResponse(content)

def write_file(request):
    if request.method == "POST":
        json_data = json.loads(request.body)
        docker_write_file('/tmp/reaudev/'+str(request.session.get('id_user'))+'/'+str(json_data['id_project'])+'/'+str(json_data['filename']), json_data['content'])
    return HttpResponse("OK")
    
def editor(request):
    if request.session.get('id_user') and request.method == "GET":
        user = User.objects.filter(id=request.session.get('id_user'))[0]
        user.password_b64 = str(base64.b64encode(user.password.encode('ascii')), "utf-8")
        project = Project.objects.filter(id=request.GET['id'])[0]
        project.owner = User.objects.filter(id=User_Project.objects.filter(id_project=project.id, role=1)[0].id_user)[0]
        files = str(docker_ls('/home/'+str(request.session.get('id_user'))+'/'+str(project.id))[1], "utf-8").split('\n')
        files.pop(len(files)-1)
        print(files)
        return render(request, 'ide/editor.html', {'user': user, 'project': project, 'files': files})
    
def create_project(request):
    if request.session.get('id_user') and request.method == "POST":
        project = Project()
        project.name = request.POST['name']
        project.type = 1
        project.status = 1
        project.save()
        user_project = User_Project()
        user_project.id_user = request.session.get('id_user')
        user_project.id_project = project.id
        user_project.role = 1
        user_project.save()
        print(docker_create_project(request.session.get('id_user'), project.id))
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