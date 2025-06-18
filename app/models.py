from . import db
from sqlalchemy.types import TypeDecorator, TEXT
import json

class IntListType(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        return json.dumps(value or [])

    def process_result_value(self, value, dialect):
        return json.loads(value or "[]")

class Zone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    zone_code = db.Column(db.Integer)
    pnus = db.Column(IntListType)
