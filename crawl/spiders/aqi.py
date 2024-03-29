#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import sys
sys.path.append("..") # Adds higher directory to python modules path.
import scrapy
import json
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
import pdb
from models import *
NUMBERICAL_COLS = ["SO2", "CO", "CO_8hr", "O3", "O3_8hr", "PM10", "PM2p5", "PM2p5_AVG", "PM10_AVG", "NO2", "NOx", "NO", "wind_speed", "wind_direction", "aqi"]
class AQISpider(scrapy.Spider):
    name = "aqi"
    

    def start_requests(self):
        url = 'http://opendata.epa.gov.tw/ws/Data/AQI/?%24format=json'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        result = json.loads(response.body_as_unicode())
        
        # easier to debug than doing it in scrapy pipeline(it's parallel there)
        for item in result:
            self.init_sites(item)
            self.insert_log(item, response)
            yield item

    def init_sites(self, item):
        # init sites, insert it if not found

        # {'SiteName': '行動監測01', 'County': '臺北市','Longitude': '', 'Latitude': '', 'SiteId': ''}
        # ....
        
        if item['SiteId'].isdigit():
            id = int(item['SiteId'])
        else:
            logging.log(logging.ERROR, "Malformed site data: " + str(item))            
            return
            
        
        if EpaAQISite.query.filter_by(site_id=id).first() == None:
            keys = ['County', 'SiteName', 'Longitude', 'Latitude']
            content = {x: item[x] for x in keys}
            content['county'] = content.pop('County')
            content['site_name'] = content.pop('SiteName')
            content['lat'] = content.pop('Latitude')
            content['lon'] = content.pop('Longitude')
            content['site_id'] = id
            newsite = EpaAQISite(content=content)

            db.session.add(newsite)
            db.session.commit()
    
    #check if the new log existed in db, insert if not
    def insert_log(self, item, response):
        pub_time = datetime.datetime.strptime(item['PublishTime'], '%Y-%m-%d %H:%M')
        if not item['SiteId'].isdigit():
            logging.log(logging.ERROR, "Malformed log data: " + str(item))  
            return 
        query = db.session.query(func.count(AQILogs.id)).filter_by(site_id=item['SiteId']).filter(AQILogs.publish_time >= pub_time)
        
        if query.scalar() == 0:
            keys = ['AQI', 'Pollutant', 'Status', 'SO2', 'CO_8hr', 'CO',
                'O3', 'O3_8hr', 'PM10', 'PM2.5', 'NO2', 'NOx', 'NO',
                'WindSpeed', 'WindDirec', 'PM2.5_AVG', 'PM10_AVG'
            ]
            
            
            content = {x: item[x] for x in keys}
            content['site_id'] = item['SiteId']
            content['publish_time'] = pub_time
            content['aqi'] = content.pop('AQI')
            content['pollutant'] = content.pop('Pollutant')
            content['status'] = content.pop('Status')
            content['PM2p5'] = content.pop('PM2.5')
            content['PM2p5_AVG'] = content.pop('PM2.5_AVG')
            content['wind_speed'] = content.pop('WindSpeed')
            content['wind_direction'] = content.pop('WindDirec')
            
            # filter out some mysterious values, 'ND', '', '-', 
            for key in NUMBERICAL_COLS:
                if key in content and not content[key].replace('.','',1).isdigit():
                    
                    content.pop(key)
                    
            
            newlog = AQILogs(content=content)

            try:
                db.session.add(newlog)
                db.session.commit()
            except:
                # pdb.set_trace()
                pass