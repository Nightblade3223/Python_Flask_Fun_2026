from flask import jsonify


def error_response(code: str, message: str, status: int, details=None):
    payload = {"error": {"code": code, "message": message, "details": details or {}}}
    return jsonify(payload), status
