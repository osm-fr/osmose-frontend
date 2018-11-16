FROM python:2.7
MAINTAINER Frédéric Rodrigo <fred.rodrigo@gmail.com>

RUN useradd -s /bin/bash -d /data/work/osmose osmose
RUN mkdir -p /data/work/osmose/results /data/project/osmose/frontend && \
    chown -R osmose /data/work/osmose
WORKDIR /data/project/osmose/frontend
EXPOSE 20009
ENTRYPOINT ["sh", "-c", "/etc/init.d/postgresql start && cd /data/project/osmose/frontend && sudo -E -u osmose -s eval '. osmose-frontend-venv/bin/activate ; ./osmose-standalone-bottle.py'"]

RUN curl -sL http://deb.nodesource.com/setup_9.x -o nodesource_setup.sh && \
    bash ./nodesource_setup.sh && \
    apt update && \
    apt install -y --no-install-recommends \
        sudo git make gettext bzip2 \
        nodejs \
        postgresql postgresql-contrib

# Postgres
ADD ./tools/database/schema.sql /data/project/osmose/frontend/tools/database/schema.sql
USER postgres
RUN /etc/init.d/postgresql start && \
    createuser osmose && \
    psql -c "ALTER ROLE osmose WITH PASSWORD '-osmose-'" && \
    createdb -E UTF8 -T template0 -O osmose osmose_frontend && \
    psql -c "CREATE extension hstore" osmose_frontend && \
    cd /data/project/osmose/frontend && \
    PGPASSWORD='-osmose-' psql -f tools/database/schema.sql -h localhost osmose_frontend osmose && \
    curl http://osmose.openstreetmap.fr/export/osmose-menu.sql.bz2 | bzcat | PGPASSWORD='-osmose-' psql -h localhost osmose_frontend osmose

# Osmose Frontend
USER root
ADD ./requirements.txt /data/project/osmose/frontend/requirements.txt
RUN virtualenv --python=python2.7 osmose-frontend-venv && \
    . osmose-frontend-venv/bin/activate && \
    pip install -r requirements.txt

ADD ./package.json /data/project/osmose/frontend
ADD ./package-lock.json /data/project/osmose/frontend
ADD ./webpack.config.js /data/project/osmose/frontend
ADD ./static /data/project/osmose/frontend/static
RUN npm install && \
    npm run build

ADD . /data/project/osmose/frontend
RUN cd po && \
    make mo

#RUN apt remove -y --auto-remove \
#        git gettext make nodejs bzip2 && \
#    rm -rf /var/lib/apt/lists/* && \
#    rm node_modules

RUN chown -R osmose /data/project/osmose
