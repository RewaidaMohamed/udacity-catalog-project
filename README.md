
# Project: Linux Server Configuration

### IP Address: 18.184.35.98
### SSH port: 2200

### URL to web application: http://18.184.35.98.xip.io/

## Server Configurations:
-create linux server instance using Amazon Lightsail

- make sure all system packages up-to-date
```
$ sudo apt-get update
$ sudo apt-get upgrade
```

## Security and Firewall Configrations:
- create new user grader(genrate public and private Keys) 
```
$ sudo adduser grader
```

- disable root login, from /etc/ssh/sshd_config I edited PermitRootLogin and set it with no.
```
PermitRootLogin no
```

-give sudo access to grader user 
edit the sudoers file, add line grader ALL=(ALL:ALL) ALL

- change ssh port to 2200
edit /etc/ssh/sshd_config and change port 22 to 2200 then restart sshd

-Allowing connection only for ssh, http and ntp using ufw commands
```
$ sudo ufw default deny incoming
$ sudo ufw default allow outcoming 
$ sudo ufw allow 2200
$ sudo ufw allow www
$ sudo ufw allow ntp
$ sudo ufw enable
$ sudo ufw status
```
## Web Application deployment to server:

- install all required packages
```
$ sudo apt-get -y install python3 python3-venv
$ sudo apt-get install python-flask
```
- install apache2 and mod-wsgi
```
$ sudo apt-get install apache2
$ sudo apt-get install libapache2-mod-wsgi
```
- install git and clone my repo to /var/www/

- change directory to my project file & create a wsgi file named application.wsgi

- add following lines to application.wsgi
```
import sys
sys.path.insert(0, '/var/www/udacity-catalog-project/catalog')
from application import app as application
application.secret_key = 'super_super_secret_key'
```
## Apache Configrations:

- in /etc/apache2/sites-available, add new file named catalog.conf and add following line secret_key
```
<VirtualHost *:80>
     # Add machine's IP address (use ifconfig command)
     ServerName 18.184.35.98
     ServerAdmin eng.rewaida2013@gmail.com
     # Give an alias to to start your website url with
     WSGIScriptAlias / /var/www/udacity-catalog-project/catalog/application.wsgi
     <Directory /var/www/udacity-catalog-project/catalog/>
            # set permissions as per apache2.conf file
            Order allow,deny
            Allow from all
     </Directory>
     ErrorLog ${APACHE_LOG_DIR}/error.log
     LogLevel warn
     CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
- change the default page with app.
```
$ sudo a2dissite 000-default.conf
$ sudo a2ensite catalog.conf
$ sudo service apache2 reload
```
## Database Setup

- for database server, install PostgreSQL 
```
$ sudo apt-get install postgresql
```
- create user and new data base, then give the user privileges.
```
$ sudo su - postgres
postgres $ psql
postgres=# CREATE DATABASE library;
CREATE USER catalog;
ALTER ROLE catalog WITH PASSWORD 'catalog'
GRANT ALL PRIVILEGES ON DATABASE library TO catalog;
```
- then changed the line with create_engine in my code to 
```
create_engine('postgresql://catalog:catalog@localhost/library')
```
## Acknowledgments
* [mudspringhiker blog](https://mudspringhiker.github.io/deploying-a-flask-web-app-on-lightsail-aws.html)
* [mod_wsgi (Apache)](http://flask.pocoo.org/docs/1.0/deploying/mod_wsgi/)
* [DigitalOcean PostgreSql tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-14-04)
