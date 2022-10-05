from enum import Enum, unique
from sqlalchemy.orm import relationship, backref

from web import db
from web import sqltype
from web.models.org import Org


@unique
class RecordType(Enum):
    none = 0
    version = 1
    toggle = 2


@unique
class RecordStatus(Enum):
    processing = 1
    finished = 2
    failed = 3


class Record(db.Model):
    __tablename__ = 'record'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(sqltype.Enum(RecordType), default=RecordType.none)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    status = db.Column(sqltype.Enum(RecordStatus), default=RecordStatus.processing)
    completeness = db.Column(db.DECIMAL(5, 2), default="0")

    record_data_rows = db.relationship('RecordData', lazy='joined',
                                       backref=backref('record_data_rows'))


class RecordData(db.Model):
    __tablename__ = 'record_data'

    id = db.Column(db.Integer, primary_key=True)

    org_id = db.Column(db.Integer, db.ForeignKey('org.id'), nullable=False)
    org = relationship(Org.__name__, foreign_keys=[org_id])

    record_id = db.Column(db.Integer, db.ForeignKey('record.id'), nullable=False)
    record = relationship(Record.__name__, foreign_keys=[record_id])

    data = db.Column(sqltype.JsonObject(db.Text))
