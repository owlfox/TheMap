from flask_sqlalchemy import SQLAlchemy
import datetime

from main import db

class EpaAQISite(db.Model):
    __tablename__ = 'epa_aqi_sites'
    id = db.Column(db.Integer, primary_key=True)
    
    site_id = db.Column(db.Integer)
    site_name = db.Column(db.String(64))
    county = db.Column(db.String(64))
    lat = db.Column(db.String(64))
    lon = db.Column(db.String(64))

    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, content):
        for key, value in content.items():
            setattr(self, key, value)

class AQILogs(db.Model):
    __tablename__ = 'aqi_logs'
    id = db.Column(db.Integer, primary_key=True)

    aqi = db.Column(db.Integer)
    site_id = db.Column(db.Integer)
    publish_time = db.Column(db.DateTime)
    status = db.Column(db.String(64))
    pollutant = db.Column(db.String(64))

    SO2 = db.Column(db.REAL())
    CO = db.Column(db.REAL())
    CO_8hr = db.Column(db.REAL())
    O3 = db.Column(db.REAL())
    O3_8hr = db.Column(db.REAL())
    PM10 = db.Column(db.REAL())
    PM2p5 = db.Column(db.REAL())
    PM2p5_AVG = db.Column(db.REAL())
    PM10_AVG = db.Column(db.REAL())
    NO2 = db.Column(db.REAL())
    NOx = db.Column(db.REAL())
    NO = db.Column(db.REAL())
    wind_speed = db.Column(db.REAL())
    wind_direction = db.Column(db.REAL())
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    
    def __init__(self, content):
        for key, value in content.items():
            setattr(self, key, value)