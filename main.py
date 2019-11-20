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
    For source data details, see https://opendata.epa.gov.tw/Data/Details/AQI/ 
    updated at 2019-11-20 12:18
    """,
    doc='/aqi/'
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
            return Response("Validation Error", status=400)
        
        last_pub_time = db.session.query(models.AQILogs.publish_time
                    ).filter(models.AQILogs.id == db.session.query(func.max(models.AQILogs.id))
                    ).first()[0]
        
        logs = db.session.query(
            models.AQILogs.publish_time,
            models.AQILogs.aqi
                    ).filter(models.AQILogs.site_id == site_id
                    ).filter(models.AQILogs.publish_time >= (last_pub_time - t)
                    ).all()
        
        
        rtn = []
        dic = {}
        for log in logs:
            # dic = log.__dict__
            # dic.pop("_sa_instance_state") # don't know why there's such key
            # dic.pop("id") # don't know why there's such key yyyy-mm-ddThh:mm:ss+zz
            dic = log._asdict()
            
            # format: 2019-11-19T04:55:00+0000
            dic['Time (UTC)'] = dic.pop('publish_time').strftime("%Y-%m-%dT%H:%M:%S+0800")
            rtn.append(dic)
        return send_csv(rtn, "rtn.csv" ,dic.keys() , cache_timeout=0)


@ns.route('/sites')
class Sites(Resource):
    @ns.doc('get sites information with current aqi, the pollutant and etc.')
    @ns.produces(["text/csv"])
    def get(self):
        
        epasites = db.session.query(
                    models.EpaAQISite.site_name,
                    models.EpaAQISite.site_id,
                    models.EpaAQISite.county,
                    models.EpaAQISite.lon,
                    models.EpaAQISite.lat,
                    ).filter(models.EpaAQISite.site_id >= 0).all()
        # todo: fix foreign key... and just join it
        last_pub_time = db.session.query(models.AQILogs.publish_time
                        ).filter(models.AQILogs.id == db.session.query(func.max(models.AQILogs.id))
                        ).first()[0]
        lastlogs = db.session.query(models.AQILogs).distinct(models.AQILogs.site_id
                        ).filter(models.AQILogs.publish_time >= last_pub_time
                        ).all()
        lastlogs_dic = {l.site_id: l for l in lastlogs}
        
        rtn = []
        result = {} # keys of to_csv argument
        for site in epasites:
            dic = site._asdict()
            dic['Lon'] = dic.pop('lon')
            dic['Lat'] = dic.pop('lat')
            
            # 'join' the latest log to show current site info...
            the_log = lastlogs_dic[dic['site_id']]
            the_dic = the_log.__dict__
            for e in ['created_at', '_sa_instance_state', 'id']:
                the_dic.pop(e)
            result = {**dic, **the_dic}
            
            rtn.append(result)
        
        return send_csv(rtn, "sites.csv" ,result.keys() , cache_timeout=0)


    

if __name__ == '__main__':
    # app.run(debug=True)
    app.run()