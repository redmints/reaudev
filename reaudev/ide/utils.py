from ide.models import User
from ide.models import Project
from ide.models import User_Project

def get_projects(id_user):
    pid = []
    for project in User_Project.objects.filter(id_user=id_user):
            pid.append(project.id)
    projects = Project.objects.filter(id__in=pid)
    for project in projects:
          project.owner = User.objects.filter(id=User_Project.objects.filter(id_project=project.id, role=1)[0].id_user)[0]
    return projects