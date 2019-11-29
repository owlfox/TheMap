# Summary
A web GIS app based on TerriaJS, for the frontend code see [this repo](https://github.com/owlfox/TerriaMap/tree/taiwan). At the moment it is capable of showing:
* data of https://airtw.epa.gov.tw/
* 3d tileset of Taichung City, Taiwan.

This repo includes the postgresSQL, crawler(by scrapy), nginx and the corresponding ansible playbooks.
* postgres resides in a separated VM called db for easy monitoring (hopefully).
* the other vm contains nginx, flask api, scrapy crawler.
* nearly all the ansible yaml files to automate deploying, excluding TLS cert, pm2 startup 


# run individual module

# crawler
0. `pip install -r requirements.txt --user` or with `venv`, then install `scrapy` separately.(It's weired that scrapy need root access to install, probably a bug)
1. copy the `config.py.example` to `config.py`, it uses sqlite by default.
2. install the pip packages in requirements and scrapy
3. `python3 manage.py db init && python3 manage.py db migrate && python3 manage.py db upgrade` to migrate the db, a `temp.db` sqlite file should be in there. 
4. then run `scrapy crawl aqi` in the project folder, to crawl data

## flask api document with openapi/swagger
See http://map.owlfox.org/aqi for api information, basically all of them returns formated csv required by terriaJS.

run
```
FLASK_APP=main.py FLASK_DEBUG=1 python3 -m flask run -h 0.0.0.0
```
http://localhost:5000/aqi to debug the api

# deploy with ansible
* configure `hosts`, `secrets.yml`, `ansible.cfg` with your sectets, keys and hostnames.
* ssh forward is required, and the key must be able clone the git repo, please update `ansible/roles/web_and_crawler/vars/main.yml` accordingly.
```
ansible-playbook deploy.yml
```
to deploy.
* `vagrant up` if you prefer to try it locally with virtualbox, the config file is `Vagrantfile`.



# db schema
see models.py, two tables, one for sites, one for logs of sites.

# TLS/HTTPS
use let'sencrypt certbot, and enable systemd timer to automate certificate update.

# shapefile to citygml
see `scripts/shp2citygml.py` for the script to transform file that cesium Ion (A 3d tile service, looks like they haven't open the tile server yet.)


# TODO
* backup
* monitor
* PM2 ansible yml
* seprate crawler into another instance
* find a better way to stream 3d tiles, vendor locked with cesiumIon

