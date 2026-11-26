import sqlite3

from flask import current_app, jsonify, request
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    def __init__(self, message, status=400, details=None):
        super().__init__(message)
        self.message, self.status, self.details = message, status, details


def error_response(message, status, details=None):
    body = {'error': {'code': status, 'message': message}}
    if details:
        body['error']['details'] = details
    return jsonify(body), status


def _is_api():
    return request.path.startswith('/api/')


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(e):
        return error_response(e.message, e.status, e.details)

    @app.errorhandler(HTTPException)  # 404, 405, 413 тощо
    def handle_http_error(e):
        if not _is_api():
            return e
        return error_response(e.description, e.code)

    @app.errorhandler(sqlite3.IntegrityError)  # страховка: дубль, FK
    def handle_integrity(e):
        if not _is_api():
            raise e
        return error_response("Конфлікт даних: дубль або запис пов'язаний з іншими", 409)

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        if not _is_api():
            raise e
        current_app.logger.exception(e)
        return error_response('Внутрішня помилка сервера', 500)
