FROM ubuntu:16.04

MAINTAINER Frédéric Rodrigo <fred.rodrigo@gmail.com>

RUN apt update && \
    apt install -y --no-install-recommends \
        curl && \
    curl -sL http://deb.nodesource.com/setup_9.x -o nodesource_setup.sh && \
    bash ./nodesource_setup.sh && \
    apt update


# Osmose Frontend

RUN mkdir -p /data/work/osmose/results
RUN useradd -s /bin/bash -d /data/work/osmose osmose
RUN chown -R osmose /data/work/osmose

RUN apt install -y --no-install-recommends \
        git gettext make nodejs

ADD "." "/data/project/osmose/frontend"
RUN chown -R osmose /data/project/osmose/frontend
USER osmose
WORKDIR "/data/project/osmose/frontend"
RUN cd /data/project/osmose/frontend && \
    npm install && \
    npm run build && \
    sed -e 's_= "osmose.openstreetmap.fr"_= "/"_' -i tools/utils.py && \
    cd po && make mo

USER root
RUN apt remove -y --auto-remove \
        git gettext make nodejs


# Python

RUN apt install -y --no-install-recommends \
        python2.7 python2.7-dev virtualenv gcc pkg-config libpng-dev libjpeg-dev libfreetype6-dev

RUN cd /data/project/osmose/frontend && \
    virtualenv --python=python2.7 osmose-frontend-venv && \
    . osmose-frontend-venv/bin/activate && \
    pip install -r requirements.txt

RUN apt remove -y --auto-remove \
        python2.7-dev gcc pkg-config


# Postgres

RUN apt install -y --no-install-recommends \
        postgresql postgresql-contrib
# postgresql-9.5-postgis-2.2

USER postgres
RUN /etc/init.d/postgresql start && \
    createuser osmose && \
    psql -c "ALTER ROLE osmose WITH PASSWORD '-osmose-'" && \
    createdb -E UTF8 -T template0 -O osmose osmose_frontend && \
    psql -c "CREATE extension hstore" osmose_frontend && \
    cd /data/project/osmose/frontend && \
    PGPASSWORD='-osmose-' psql -f tools/database/schema.sql -h localhost osmose_frontend osmose


# Apache

USER root
#RUN apt install -y --no-install-recommends \
#        apache2 libapache2-mod-wsgi

#RUN cd /data/project/osmose/frontend && \
#    cp apache-site /etc/apache2/sites-available/osmose.conf

#RUN a2dissite 000-default.conf && \
#    a2ensite osmose.conf && \
#    a2enmod expires.load && \
#    a2enmod rewrite.load

#RUN ln -sfT /dev/stdout /var/log/apache2/access.log && \
#    ln -sfT /dev/stderr /var/log/apache2/error.log && \
#    ln -sfT /dev/stdout /var/log/apache2/other_vhosts_access.log && \
#    ln -sfT /dev/stdout /var/log/apache2/osmose-access.log && \
#    ln -sfT /dev/stderr /var/log/apache2/osmose-error.log


RUN apt install sudo

RUN rm -rf /var/lib/apt/lists/*

#EXPOSE 80
#ENTRYPOINT ["sh", "-c", "/etc/init.d/postgresql start && /usr/sbin/apachectl -D FOREGROUND"]

EXPOSE 20009
ENTRYPOINT ["sh", "-c", "/etc/init.d/postgresql start && cd /data/project/osmose/frontend && sudo -E -u osmose -s eval '. osmose-frontend-venv/bin/activate ; ./osmose-standalone-bottle.py'"]
