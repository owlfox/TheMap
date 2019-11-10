# the_map

# aqi crawler
a simple scrapy spider to crawl api API and save them to postgres or sqlite(for testing)

# how to use
### use vagrant up to run it in your local vm
`vagrant up && ansible-playbook aqi.yml`


### if you want to run it directly...
1. copy the config.py.example to config.py
2. install the pip packages in requirements and scrapy
3. `python3 manage.py db init && python3 manage.py db migrate && python3 manage.py db upgrade` to init db 
4. then run `scrapy crawl aqi` in the project folder

a `temp.db` sqlite file should be in there.

# db schema
see models.py

