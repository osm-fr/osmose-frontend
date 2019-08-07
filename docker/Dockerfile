FROM python:2.7
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

ADD ./package.json /data/project/osmose/frontend
ADD ./package-lock.json /data/project/osmose/frontend
ADD ./webpack.config.js /data/project/osmose/frontend
ADD ./static /data/project/osmose/frontend/static
RUN mkdir ../node_modules && \
    ln -s ../node_modules node_modules && \
    npm install
RUN npm run build

ADD po /data/project/osmose/frontend/po
RUN cd po && \
    make mo && \
    cd ..

ADD . /data/project/osmose/frontend

ENV LANG en_US.UTF-8
CMD ./osmose-standalone-bottle.py
EXPOSE 20009
