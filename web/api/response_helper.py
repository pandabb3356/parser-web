from flask import jsonify


def _message(message, code):
    return jsonify({'message': message}), code


def not_found_error(message='Not Found'):
    return _message(message, 404)


def conflict_error(message=''):
    return _message(message, 409)


def bad_request_error(message=''):
    return _message(message, 400)


def internal_server_error(message=''):
    return _message(message, 500)


def bad_request_with_data(data=None):
    return jsonify(data or {}), 400


def forbidden_error(message=''):
    return _message(message, 403)


def authentication_failed(message=''):
    return _message(message, 401)


def validation_failed(errors=None, message=None):
    obj = {'errors': errors or {}}
    if message:
        obj['message'] = message
    return jsonify(obj), 400


def success_with_message(message="", status_code=200):
    return _message(message, status_code)


def success(data=None):
    return jsonify(data or {}), 200


def creation_success(data=None):
    return jsonify(data or {}), 201


def object_not_found(message):
    return _message(message, 204)
