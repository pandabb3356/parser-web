from flask_restful import fields

from web.constants import DATETIME_FORMAT, DATE_DISPLAY_FORMAT


class Date(fields.Raw):
    def format(self, value):
        if type(value) is str:
            return value

        try:
            return value.strftime(DATE_DISPLAY_FORMAT)
        except AttributeError as ae:
            raise fields.MarshallingException(ae)


class Datetime(fields.Raw):
    def format(self, value):
        if type(value) is str:
            return value

        try:
            return value.strftime(DATETIME_FORMAT)
        except AttributeError as ae:
            raise fields.MarshallingException(ae)


class Enum(fields.Raw):
    def format(self, value):
        if type(value) is str:
            return value

        try:
            return value.name
        except AttributeError as ae:
            raise fields.MarshallingException(ae)


org_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'protocol': fields.String,
    'domain': fields.String,
    'public_cloud': fields.Boolean,
    'tc_default_org_id': fields.Integer,
}

record_data_fields = {
    'id': fields.Integer,
    'data': fields.Raw,
    'record_id': fields.Integer,
    'org_id': fields.Integer,
    'org': fields.Nested(org_fields)
}

record_fields = {
    'id': fields.Integer,
    'type': Enum,
    'created_at': Datetime,
    'status': Enum,
    'completeness': fields.String,
    'record_data_rows': fields.List(fields.Nested(record_data_fields)),
}

service_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'key': fields.String,
    'type': Enum
}

toggle_fields = {
    'id': fields.Integer,
    'feature_toggle_name': fields.String,
    'default_value': fields.Boolean,
    'description': fields.String,
}
