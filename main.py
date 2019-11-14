from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

from flask_restplus import Api, Resource, fields
import models
import pdb
from flask_csv import send_csv
from marshmallow import Schema, fields
app = Flask(__name__)
SQLALCHEMY_DATABASE_URI='sqlite:///temp.db'
app.config.from_object('config')


db = SQLAlchemy(app)




api = Api(app)

@api.route('/aqi')
class AQI(Resource):
    def get(self):
        return {'hello': 'world'}

class SiteSchema(Schema):
    site_id = fields.Integer()
    site_name = fields.Str()
    created_at = fields.DateTime()
    county = fields.Str()
    lat = fields.Str()
    lon = fields.Str()

@api.route('/sites')
class Sites(Resource):
    def get(self):
        epasites = models.EpaAQISite.query.filter(EpaAQISite.site_id >= 0)
        # don't know why there's such key
        keys = [k  for  k in  epasites[0].__dict__.keys() if k != "_sa_instance_state"]
        rtn = []
        for site in epasites:
            dic = site.__dict__
            dic.pop("_sa_instance_state")
            rtn.append(dic)
        
        return send_csv(rtn, "rtn.csv" ,keys , cache_timeout=0)


    

if __name__ == '__main__':
    app.run(debug=True)