from django.core.management.base import BaseCommand, CommandError
from ide.models import User
from ide.models import Group
from ide.models import User_Group
from ide.utils import docker_create_user
import csv
import hashlib
from unidecode import unidecode


class Command(BaseCommand):
    help = "Import users from a Pronote CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)
        parser.add_argument("group_name", type=str)

    def handle(self, *args, **options):
            with open(options["csv_file"], 'r') as file:
                csvreader = csv.reader(file, delimiter=';')
                header = next(csvreader)
                main_group = Group.objects.filter(name=options["group_name"])
                if not main_group:
                    main_group = Group()
                    main_group.name = options["group_name"]
                    main_group.save()
                else:
                     main_group = main_group[0]
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
                        ug = User_Group()
                        ug.user = user
                        ug.group = main_group
                        ug.save()
                        if row[4] != main_group.name:
                            group = Group.objects.filter(name=row[4])
                            if not group:
                                group = Group()
                                group.name = row[4]
                                group.save()
                            else:
                                group = group[0]
                            ug = User_Group()
                            ug.user = user
                            ug.group = group
                            ug.save()
                        self.stdout.write(self.style.SUCCESS('[OK] '+name+' '+email+' '+password))
                    else:
                        continue