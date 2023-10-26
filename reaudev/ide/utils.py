from ide.models import User
from ide.models import Project
from ide.models import User_Project
import docker
import crypt
import os

def docker_exec(id_container, cmd):
      client = docker.from_env()
      container = client.containers.get(id_container)
      return container.exec_run(cmd)

def docker_create_user(id_user, password):
    cmd = 'useradd -s /bin/bash -d /home/'+str(id_user)+' -m -p '+crypt.crypt(str(password))+' "'+str(id_user)+'"'
    return docker_exec('0581dd23c4f3', cmd)

def docker_create_project(id_user, id_project):
      return docker_exec('0581dd23c4f3', 'mkdir /home/'+str(id_user)+'/'+str(id_project))

def docker_cat(path):
      return docker_exec('0581dd23c4f3', 'cat '+str(path))

def docker_rm(path):
      os.remove(path)

def docker_ls(path):
      return docker_exec('0581dd23c4f3', 'ls '+str(path))

def docker_touch(path):
      file = open(path, 'w')
      file.close()
      return file

def docker_write_file(path, content):
      file = open(path, 'w')
      file.write(content)
      file.close()
      return file