from django.shortcuts import render
from django.shortcuts import redirect
from ide.models import User
from ide.models import Project
from ide.models import User_Project
from ide.utils import get_projects

# Create your views here.

def home(request):
    if request.session.get('id_user'):
        user = User.objects.filter(id=request.session.get('id_user'))[0]
        projects = get_projects(user.id)
        return render(request, 'ide/home.html', {'user': user, 'projects': projects})
    else:
        return redirect("/login")
    
def editor(request):
    if request.session.get('id_user') and request.method == "GET":
        user = User.objects.filter(id=request.session.get('id_user'))[0]
        project = Project.objects.filter(id=request.GET['id'])[0]
        project.owner = User.objects.filter(id=User_Project.objects.filter(id_project=project.id, role=1)[0].id_user)[0]
        return render(request, 'ide/editor.html', {'user': user, 'project': project})
    
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
    return redirect("/")

def signup(request):
    if request.method == "POST":
        user = User()
        form = request.POST
        if not User.objects.filter(email=form['email']):
            user.username = form['name']
            user.email = form['email']
            user.password = form['password']
            user.type = 0
            user.save()
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
        if user.password == form['password']:
            request.session['id_user'] = user.id
            return redirect("/")
        else:
            return redirect("/login")
    else:
        return render(request, 'ide/login.html')