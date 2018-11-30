# airline
### Requirements

- Python 3.x
- Mysql 5.7 or higher 

### Guide d'installation
    
    -  Vous pouvez cloner le projet depuis github.
    -  Vous pouvez aussi utiliser le dossier airline fournit avec le fichier zip.

    $  git clone https://github.com/MehdiAdim/airline.git
    $  cd chemin_d_acces/airline

    1- Installation des exigences:

    $  pip install -r requirements.txt
    #  Si vous avez pas les droits utilisez :
    $  pip install --user -r requirements.txt
   
    2- Modification de configuration:
       Acceder au fichier config.py :
       En modifiant les champs suivants convenablement avec vos parametres MYSQL 
       MYSQL_DATABASE_USER
       MYSQL_DATABASE_PASSWORD 
       MYSQL_DATABASE_HOST
    
    3- Ensuite importez et exécutez le fichier schema.sql dans votre application de gestion de SGBD MYSQL 
       (phpMyAdmin or Mysql workbench) pour la creation des tables et l'insertion de donnees.
    
    4- Finalement demarrez l'application web :
    $  python run.py
    
    5- Visitez http://127.0.0.1:5000 
       Vous pouvez s'hautentifier comme admin avec username = admin et password = admin.
       Et vous pouvez créer votre compte client dans la page d'enregistrement.
       

