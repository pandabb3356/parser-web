import abc
import datetime

from web import db
from web.models.org import Org
from web.models.record import Record, RecordStatus, RecordData


class BaseParser(abc.ABC):
    DEFAULT_TIMEOUT: int = 60

    def __init__(self, record_id, selected_org_ids=None):
        query = Org.query
        if isinstance(selected_org_ids, list) and len(selected_org_ids) > 0:
            query = query.filter(Org.id.in_(selected_org_ids))

        self.orgs = query.all()

        self.record_id = record_id
        self.record = Record.query.get(record_id)

        self.records_data = []

        self.failed_orgs = []
        self.finished_orgs = []

    @staticmethod
    def create_record(record_type):
        record = Record(status=RecordStatus.processing, type=record_type, created_at=datetime.datetime.utcnow())
        db.session.add(record)
        db.session.flush()
        db.session.commit()

        return record

    @abc.abstractmethod
    def fetch_data(self):
        pass

    def add_record_data(self, data, org_id):
        record_data = RecordData(record_id=self.record_id, data=data, org_id=org_id)

        db.session.add(record_data)
        db.session.flush()

        return record_data

    def update_record_completeness(self):
        self.record.completeness = 100 if not len(self.orgs) \
            else round((len(self.finished_orgs) / len(self.orgs)) * 100, 2)

    def mark_record_finished(self):
        self.record.status = RecordStatus.finished
        db.session.flush()
        db.session.commit()

    def do_services(self):
        self.fetch_data()
        self.mark_record_finished()
