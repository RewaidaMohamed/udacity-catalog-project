import sys
sys.path.insert(0, '/var/www/udacity-catalog-project/catalog')
from application import app as application
application.secret_key = 'super_super_secret_key'
