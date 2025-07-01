from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

class Map(db.Model):
    map_id = db.Column(db.Integer, primary_key=True)
    map_code = db.Column(db.Integer, nullable=False)
    zone_code = db.Column(db.Integer, nullable=False)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)

class Place(db.Model):
    pnu = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String, nullable=False)

class Grass(db.Model):
    grass_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    map_id = db.Column(db.Integer, db.ForeignKey('map.map_id'), nullable=False)
    pnu = db.Column(db.BigInteger, db.ForeignKey('place.pnu'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

class SubZone(db.Model):
    sub_zone_code = db.Column(db.Integer, primary_key=True)
    map_id = db.Column(db.Integer, db.ForeignKey('map.map_id'), nullable=False)
