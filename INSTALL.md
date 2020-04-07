Manual Installation
-------------------

### Dependencies

For Ubuntu Server 16.04

```
apt install python2.7 python2.7-dev virtualenv gcc pkg-config libpng-dev libjpeg-dev libfreetype6-dev postgresql-server-dev-all libgeos-dev g++ python-shapely nodejs npm
```

#### Database

```
apt install postgresql postgresql-contrib
```

#### Web server

```
apt install apache2 libapache2-mod-wsgi
```

#### Internationalisation and SVG rendering

```
apt install gettext librsvg2-bin
```

### Initialisation

Generate translation files
```
(cd web/po && make mo)
```


### Python

Osmose QA frontend requires python > 2.6 and < 3

Create a python virtualenv, active it and install python dependencies
```
virtualenv --python=python2.7 osmose-frontend-venv
source osmose-frontend-venv/bin/activate
pip install -r requirements.txt
```

Generate markers
```
(cd tools && ./make-markers.py)
```


### JavaScript

Install javascript libraries with npm
```
(cd web && npm install && npm run build)
```


### Database

As postgres user:
```
createuser -s osmose
# Set your own password
psql -c "ALTER ROLE osmose WITH PASSWORD '-osmose-';"
createdb -E UTF8 -T template0 -O osmose osmose_frontend
# Enable extensions
psql -c "CREATE EXTENSION pgcrypto" osmose_frontend
```

As normal user, create the database tables:
```
psql osmose_frontend -f tools/database/schema.sql
```

Check data base parameter into `tools/utils.py`.


### Web Server

As root user, copy `apache-site` to `/etc/apache2/sites-available/osmose.conf`.
Adjust the config, if needed. Especially the user and group running the process in
`WSGIDaemonProcess` and `WSGIProcessGroup`, and path in `WSGIScriptAlias`,
`DocumentRoot`, `Alias`s and `Directory`.

If you setup a python virtualenv add the appropriate `python-path=/home/osmose/osmose-frontend-venv/lib/python2.7/site-packages`
at the and of WSGIDaemonProcess line.

Enable the new config:
```
a2dissite 000-default.conf
a2ensite osmose.conf
a2enmod expires.load
a2enmod rewrite.load
service apache2 reload
```

Change the server URL into `website` in file `tools/utils.py`.


Database translations
---------------------

When some issues are in the database, to get translations
```
cd tools/database/ && ./categ_menu_update.sh && ./item_menu_update.sh
```

Add "tools/cron.sh" to crontab, to run once per day.
