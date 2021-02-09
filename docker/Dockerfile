FROM python:3.7
MAINTAINER Frédéric Rodrigo <fred.rodrigo@gmail.com>

RUN mkdir -p /data/work/root/results/

RUN curl -sL http://deb.nodesource.com/setup_12.x -o nodesource_setup.sh && \
    bash ./nodesource_setup.sh && \
    apt update && \
    apt install -y --no-install-recommends \
        bzip2 \
        gettext \
        git \
        make \
        nodejs \
        postgresql-client \
        sudo && \
    apt-get clean

ADD ./requirements.txt /data/project/osmose/frontend/requirements.txt
WORKDIR /data/project/osmose/frontend
RUN pip install -r requirements.txt

RUN mkdir /data/project/osmose/frontend/web
ADD ./web/package.json /data/project/osmose/frontend/web/
ADD ./web/package-lock.json /data/project/osmose/frontend/web/
ADD ./web/webpack.config.js /data/project/osmose/frontend/web/
RUN mkdir ../node_modules && \
    ln -s ../../node_modules web/node_modules && \
    cd web && \
    npm install

ADD . /data/project/osmose/frontend
RUN cd web && npm run build
RUN cd web/po && \
    make mo && \
    cd ..

ENV LANG en_US.UTF-8
CMD ./osmose-standalone-bottle.py
EXPOSE 20009
