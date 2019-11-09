# the_map

# db migration
```
python flask_aqi/manage.py db init
python flask_aqi/manage.py db migrate
python flask_aqi/manage.py db upgrade

<!-- when something wrong -->
python flask_aqi/manage.py db --help 
```
change the config in manage.py to postgresql if needed