from ide.models import User
from unidecode import unidecode
from ide.utils import *
import hashlib
import csv

def run():
    with open("scripts/file.csv", 'r') as file:
        csvreader = csv.reader(file, delimiter=';')
        header = next(csvreader)
        for row in csvreader:
            name = row[0]
            email = unidecode(row[0].lower()).replace(" ", "")+"@reaudev.redmints.fr"
            password = str(row[2].replace("/", ""))
            user = User()
            if not User.objects.filter(email=email):
                user.username = name
                user.email = email
                user.password = hashlib.sha256(password.encode('utf-8')).hexdigest()
                user.type = 0
                user.save()
                print(docker_create_user(user.id, user.password))
                print('[OK] '+name+' '+email+' '+password)
            else:
                continue