from flask import request
from flask_restful import marshal
from sqlalchemy.orm import subqueryload

from web import instant_jobs_queue, db
from web.api import bp
from web.api.response_helper import success, creation_success, bad_request_error
from web.api.resource_fields import record_fields, record_data_fields, service_fields, toggle_fields
from web.models.record import RecordData
from web.models.service import ServiceType, Service
from web.models.record import Record, RecordType, RecordStatus
from web.models.toggle import TronClassToggle
from web.parser.toggles_parser import TogglesParser
from web.parser.toggles_excel import prepare_orgs_toggles_dfs
from web.parser.versions_parser import VersionsParser
from web.parser.versions_excel import prepare_orgs_versions_dfs
from web.task import BaseTask
from web.util import make_df_excel_response, generate_current_time_for_file_name


def parse_versions_perform_func(record_id):
    version_parser = VersionsParser(record_id=record_id)
    version_parser.do_services()


@bp.route('/parser/versions-parser/record', methods=["POST"])
def parse_orgs_versions():
    processing_record = Record.query.filter(Record.type == RecordType.version,
                                            Record.status == RecordStatus.processing) \
        .order_by(Record.id.desc()).first()

    if processing_record is not None:
        return bad_request_error(message='The latest record is still processing, please wait.')

    record = VersionsParser.create_record(record_type=RecordType.version)

    version_task = BaseTask(perform_func=parse_versions_perform_func)

    instant_jobs_queue.enqueue(version_task.perform, record.id)

    return creation_success({'record': marshal(record, record_fields)})


@bp.route('/parser/<string:record_type>/records', methods=["GET"])
def get_parser_records(record_type):
    try:
        rt = RecordType[record_type]
    except Exception as ex:
        rt = RecordType.version

    record_ids = (request.args.get("ids") or "")

    query = Record.query.filter(Record.type == rt).order_by(Record.created_at.desc())
    if record_ids:
        query = query.filter(Record.id.in_(list(map(int, record_ids.split(",")))))
    records = query.all()
    return success({'records': marshal(records, record_fields)})


@bp.route('/parser/versions-parser/records', methods=["GET"])
def get_versions_parser_records():
    records = Record.query.filter(Record.type == RecordType.version).order_by(Record.created_at.desc()).all()
    return success({'records': marshal(records, record_fields)})


@bp.route('/parser/toggles-parser/records', methods=["GET"])
def get_toggles_parser_records():
    records = Record.query.filter(Record.type == RecordType.toggle).order_by(Record.created_at.desc()).all()
    return success({'records': marshal(records, record_fields)})


@bp.route('/parser/versions-parser/records/<int:record_id>/record-data', methods=["GET"])
def get_versions_parser_record_data(record_id):
    record = Record.query \
        .options(subqueryload(Record.record_data_rows).joinedload(RecordData.org)) \
        .filter(Record.id == record_id).first()

    services = Service.query.filter(Service.type == ServiceType.TC).all()

    return success({
        'record': marshal(record, record_fields),
        'record_data_rows': marshal(record.record_data_rows, record_data_fields),
    })


@bp.route('/parser/toggles-parser/records/<int:record_id>/record-data', methods=["GET"])
def get_toggles_parser_record_data(record_id):
    record = Record.query \
        .options(subqueryload(Record.record_data_rows).joinedload(RecordData.org)) \
        .filter(Record.id == record_id).first()

    toggles = TronClassToggle.query.order_by(TronClassToggle.id).all()
    marshaled_toggles = marshal(toggles, toggle_fields)
    toggle_keys = set([toggle.feature_toggle_name for toggle in toggles])

    for record_data in record.record_data_rows:
        data = (record_data.data or {})
        if not isinstance(data, dict) or 'toggles-error' in data:
            continue

        for k, v in data.items():
            if k not in toggle_keys:
                marshaled_toggles.append({
                    TronClassToggle.id.name: '',
                    TronClassToggle.feature_toggle_name.name: k,
                    TronClassToggle.default_value.name: '',
                    TronClassToggle.description.name: '',
                })

                toggle_keys.add(k)

    return success({
        'record': marshal(record, record_fields),
        'record_data_rows': marshal(record.record_data_rows, record_data_fields),
        'toggles': marshaled_toggles
    })


@bp.route('/parser/records/<int:record_id>', methods=["DELETE"])
def delete_parser_record(record_id):
    record = Record.query.filter(Record.id == record_id).first()
    if record is None:
        return bad_request_error()

    for record_data in record.record_data_rows:
        db.session.delete(record_data)

    db.session.delete(record)

    db.session.commit()
    return success()


def parse_toggles_perform_func(record_id):
    version_parser = TogglesParser(record_id=record_id)
    version_parser.do_services()


@bp.route('/parser/toggles-parser/record', methods=["POST"])
def parse_orgs_toggles():
    processing_record = Record.query.filter(Record.type == RecordType.toggle,
                                            Record.status == RecordStatus.processing) \
        .order_by(Record.id.desc()).first()

    if processing_record is not None:
        return bad_request_error(message='The latest record is still processing, please wait.')

    record = TogglesParser.create_record(record_type=RecordType.toggle)

    toggle_task = BaseTask(perform_func=parse_toggles_perform_func)

    instant_jobs_queue.enqueue(toggle_task.perform, record.id)

    return creation_success({'record': marshal(record, record_fields)})


@bp.route('/parser/versions-parser/records/<int:record_id>/excel', methods=["GET"])
def get_orgs_versions_excel(record_id):
    record = Record.query.filter(Record.id == record_id).first()

    if record is None:
        return bad_request_error(message='No record!')

    if record.status == RecordStatus.processing:
        return bad_request_error(message='The record is still processing, please wait.')

    df_sets = prepare_orgs_versions_dfs(record)
    return make_df_excel_response(df_sets, file_name=f'service_versions_{generate_current_time_for_file_name()}')


@bp.route('/parser/toggles-parser/records/<int:record_id>/excel', methods=["GET"])
def get_orgs_toggles_excel(record_id):
    record = Record.query.filter(Record.id == record_id).first()

    if record is None:
        return bad_request_error(message='No record!')

    if record.status == RecordStatus.processing:
        return bad_request_error(message='The record is still processing, please wait.')

    df_sets = prepare_orgs_toggles_dfs(record)
    return make_df_excel_response(df_sets, file_name=f'toggles_{generate_current_time_for_file_name()}')
