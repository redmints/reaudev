from ide.models import User
from ide.models import Project
from ide.models import User_Project
import docker
import crypt

def get_projects(id_user):
    pid = []
    for project in User_Project.objects.filter(id_user=id_user):
            pid.append(project.id)
    projects = Project.objects.filter(id__in=pid)
    for project in projects:
          project.owner = User.objects.filter(id=User_Project.objects.filter(id_project=project.id, role=1)[0].id_user)[0]
    return projects

def docker_exec(id_container, cmd):
      client = docker.from_env()
      container = client.containers.get(id_container)
      return container.exec_run(cmd)

def docker_create_user(id_user, password):
    cmd = 'useradd -s /bin/bash -d /home/'+str(id_user)+' -m -p '+crypt.crypt(str(password))+' "'+str(id_user)+'"'
    return docker_exec('cdb68645a39b', cmd)

def docker_create_project(id_user, id_project):
      return docker_exec('cdb68645a39b', 'mkdir /home/'+str(id_user)+'/'+str(id_project))

def docker_cat(path):
      return docker_exec('cdb68645a39b', 'cat '+str(path))

def docker_ls(path):
      return docker_exec('cdb68645a39b', 'ls '+str(path))