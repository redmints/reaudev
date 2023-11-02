# reaudev

Une plateforme de développement logiciel en ligne ayant pour but l'apprentissage de la programmation au lycée.

reaudev peut s'utiliser en cours de SNT, NSI, STI2D SIN, mathématiques ou même physique et éventuellement dans d'autres disciplines.

Prod : [https://reaudev.redmints.fr]([https://reaudev.redmints.fr)

## Pré-requis

Pour faire tourner le projet sur votre environnement, vous devez au préalable :

- Avoir un répertoire de travail, dans lequel vous créez un répertoire pour les données de vos utilisateurs
- Installer docker, pip, django, virtualenv...
- ...ainsi qu'un conteneur docker : ```docker run -d -it -v <répertoire_données_utilisateurs>:/home/ -p 1222:22 python ```
- Sur ce conteneur docker, installer un serveur SSH (```apt install openssh-server && service sshd start ```)
- Installer Web SSH : ```sudo pip3 install webssh ```

## Installation

Cloner le dépôt reaudev dans votre répertoire de travail

Créer un environnement virtuel :

```bash
mkdir env
virtualenv ./env
source env/bin/activate
```

Lancer les migrations : ```python3 manage.py migrate ```

Modifier dans le fichier settings.py les variables :

- ```DOCKER_CONTAINER ``` : l'identifiant de votre conteneur précédemment créé
- ```REAUDEV_URL ``` : L'URL de votre serveur de développement
- ```DOCKER_HOST ``` : Le nom d'hôte pour accéder à votre conteneur en SSH (si en local, alors localhost)
- ```DOCKER_PORT ``` : Le port pour accéder à votre conteneur en SSH (si pas modifié aux étapes précédentes, alors 1222)
- ```SHARED_DIRECTORY ``` : Le chemin d'accès à votre répertoire pour les données utilisateurs (dans mon cas /tmp/reaudev)

Lancer le serveur : ```python3 manage.py runserver ```

## Support

Pour tout repport de bug, question sur le projet ou demande de contribution, n'hésitez-pas à ouvrir un ticket ou à m'envoyer un email à mathias.hanna@ac-nantes.fr