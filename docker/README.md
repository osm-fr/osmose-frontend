Docker
======

Build the Docker image, within the docker directory:
```
curl http://osmose.openstreetmap.fr/export/osmose-menu.sql.bz2 | bzcat > osmose-menu.sql
docker-compose build
```

Run the containers:
```
docker-compose up
```

The server will be running at http://localhost:20009/en/map/


Docker for development
----------------------

Create a container nammed `frontend` by running a configuration and password less instance:
```
docker-compose -f docker-compose.yml -f docker-compose-test.yml -f docker-compose-dev.yml run --name frontend -p 20009:20009 -p 8080:8080 frontend
```
The named container is required to be access from the backend.

Once the it is created, you can enter it again with:
```
docker-compose up -d postgres
docker start frontend && docker exec -ti frontend bash
```

Once on container, first time of for development purpose:
```
cd web
cd po && make mo && cd ..
ln -s ../../node_modules/ node_modules
npm run build
```

Then run the standalone web server
```
./osmose-standalone-bottle.py
```

To upload data to Osmose Frontend see the Osmose Backend.

Show the results at: http://localhost:20009/en/errors?item=xxxx&useDevItem=true

Acces to the database with
```
psql -h postgres osmose_frontend osmose
```
