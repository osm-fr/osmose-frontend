Docker
======

Build the Docker image, within docker directory:
```
docker build -t osm-fr/osmose_frontend:latest ..
```

Run the container:
```
docker run -ti -p 20009:20009 -e URL_FRONTEND=localhost:20009 osm-fr/osmose_frontend:latest
```

The server will be running at http://localhost:20009/en/map/


Docker for development
----------------------

Run a configuration and password less instance:
```
docker run -ti -p 20009:20009 -e URL_FRONTEND=localhost:20009 -e OSMOSE_UNLOCKED_UPDATE=on osm-fr/osmose_frontend:latest
```

Configure your Osmose Backend to point to the Osmose Frontend in `osmose-backend/modules/config.py`
```python
url_frontend_update = "http://myhost:20009/control/send-update"
```

Run the Backend with upload password `osmose-backend/osmose_config_password.py` for your analyse:
```python
def set_password(config):
  config["test"].analyser["merge_cadastre_FR"] = "MAGIC"
```

Then run the anlyse on the backend:
```
python ./osmose_run.py --skip-init --no-clean --country=test --analyser=merge_cadastre_FR
```

And show the result at: http://myhost:20009/en/errors?item=xxxx&useDevItem=true
