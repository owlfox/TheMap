# the_map

# aqi crawler
a simple scrapy spider to crawl api API and save them to postgres or sqlite(for testing)

# how to use
### use vagrant up to run it in your local vm
`vagrant up && ansible-playbook aqi.yml`


### if you want to run it directly...
1. copy the config.py.example to config.py
2. install the pip packages in requirements and scrapy
3. `python3 manage.py db init && python3 manage.py db migrate && python3 manage.py db upgrade` to init db, a `temp.db` sqlite file should be in there. 
4. then run `scrapy crawl aqi` in the project folder
5. `FLASK_APP=main.py FLASK_DEBUG=1 python -m flask run` [SRC](https://stackoverflow.com/questions/16344756/auto-reloading-python-flask-app-upon-code-changes)
6. `/docs` to see api docs

# db schema
see models.py

# links
https://github.com/noirbizarre/flask-restplus/
