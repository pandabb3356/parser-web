from enum import Enum, unique

from web import db
from web import sqltype


@unique
class ServiceType(Enum):
    TC = 1      # TronClass


class Service(db.Model):
    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Unicode(255), nullable=False)
    name = db.Column(db.Unicode(255), nullable=False)
    type = db.Column(sqltype.Enum(ServiceType), default=ServiceType.TC, nullable=False)
