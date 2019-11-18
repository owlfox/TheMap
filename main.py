from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus
from flask_restplus import Api, Resource, fields
import pdb
from flask_csv import send_csv
from sqlalchemy import func
from marshmallow import Schema, fields
import re
from datetime import timedelta, datetime

app = Flask(__name__)
SQLALCHEMY_DATABASE_URI='sqlite:///temp.db'
app.config.from_object('config')
db = SQLAlchemy(app)
import models

api = Api(app, version='1.0', title='Air Quality Index API',
    description="""it provides hitory data of epa site.
    For source data details, see https://opendata.epa.gov.tw/Data/Details/AQI/ """,
)

ns = api.namespace('aqi', description='Air Quality Index / 空氣品質資料 API')


@ns.response(HTTPStatus.NOT_FOUND, 'Site not found')
@ns.route('/<site_id>') # currently swagger will generate two engpoint for this.
@ns.route('/<site_id>/<interval>')
@ns.doc(params={'site_id': 'the epa air quality site ID',
                'interval': """currently support: blank(12hrs), <1-60>m, <1-24>h, <1-7>d, <1-4>w"""
})
class AQI(Resource):
    '''return timedelta if success else None'''
    def get_time_delta(self, site_id, interval):
        t = None

        id_match = re.match(r"^([0-9]+)$", site_id)
        if id_match != None:
            
            if interval != '':
                match = re.match(r"^([1-9]{1,2})(m|h|d|)$", interval)
                if match:
                    m1 = int(match[1])
                    if match[2] == 'm':
                        t = timedelta(minutes=m1) if not (m1 < 1 or m1 > 60) else None
                    elif match[2] == 'h':
                        t = timedelta(hours=m1) if not (m1 < 1 or m1 > 60) else None
                    elif match[2] == 'd':
                        t = timedelta(days=m1) if not (m1 < 1 or m1 > 7) else None
                    elif match[2] == 'w':
                        t = timedelta(weeks=m1) if not (m1 < 1 or m1 > 4) else None
                    t = m1 * t if t != None else None
            else:
                t = timedelta(hours=12)
        return t
        
    @api.response(200, 'Success')
    @api.response(400, 'Validation Error')
    def get(self, site_id, interval=""):
        
        t= self.get_time_delta(site_id, interval)
        if t == None:
            return Response("invalid input", status=400)
        
        last_pub_time = db.session.query(models.AQILogs.publish_time
                    ).filter(models.AQILogs.id == db.session.query(func.max(models.AQILogs.id))
                    ).first()[0]
        
        logs = db.session.query(models.AQILogs
                    ).filter(models.AQILogs.id == site_id
                    ).filter(models.AQILogs.publish_time >= (last_pub_time - t)
                    ).all()
        
        
        rtn = []
        dic = {}
        for log in logs:
            dic = log.__dict__
            dic.pop("_sa_instance_state") # don't know why there's such key
            dic.pop("id") # don't know why there's such key
            rtn.append(dic)
        
        
        return send_csv(rtn, "rtn.csv" ,dic.keys() , cache_timeout=0)

class SiteSchema(Schema):
    site_id = fields.Integer()
    site_name = fields.Str()
    created_at = fields.DateTime()
    county = fields.Str()
    lat = fields.Str()
    lon = fields.Str()

@ns.route('/sites')
class Sites(Resource):
    @ns.doc('get sites information with current aqi and the pollutant')
    @ns.produces(["text/csv"])
    def get(self):
        
        epasites = models.EpaAQISite.query.filter(models.EpaAQISite.site_id >= 0)
        # todo: fix foreign key... and just join it
        last_pub_time = db.session.query(models.AQILogs.publish_time
                        ).filter(models.AQILogs.id == db.session.query(func.max(models.AQILogs.id))
                        ).first()[0]
        logs = db.session.query(models.AQILogs).distinct(models.AQILogs.site_id
                        ).filter(models.AQILogs.publish_time >= last_pub_time
                        ).all()
        logs_dic = {l.site_id: l for l in logs}
        
        rtn = []
        for site in epasites:
            dic = site.__dict__
            dic.pop("_sa_instance_state") # don't know why there's such key
            dic.pop("updated_at")
            
            # 'join' the latest log...
            the_log = logs_dic[dic['site_id']]
            dic['aqi'] = the_log.aqi
            dic['status'] = the_log.status
            dic['pollutant'] = the_log.pollutant
            dic['wind_direction'] = the_log.pollutant
            dic['wind_speed'] = the_log.pollutant
            rtn.append(dic)
        keys = epasites[0].__dict__.keys() if len(epasites) > 0 else None
        return send_csv(rtn, "rtn.csv" ,keys , cache_timeout=0)


    

if __name__ == '__main__':
    app.run(debug=True)