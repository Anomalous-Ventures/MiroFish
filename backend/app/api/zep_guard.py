"""Fail-closed guards for routes that require the external Zep service."""

from functools import wraps

from flask import jsonify

from ..config import Config


def zep_unavailable_response():
    if not Config.USE_ZEP:
        return jsonify({
            "success": False,
            "error": "Zep integration is disabled",
        }), 503
    if not Config.ZEP_API_KEY:
        return jsonify({
            "success": False,
            "error": "ZEP_API_KEY is not configured",
        }), 503
    return None


def require_zep(route):
    """Reject Zep-dependent requests before tasks or external calls start."""

    @wraps(route)
    def guarded(*args, **kwargs):
        unavailable = zep_unavailable_response()
        if unavailable is not None:
            return unavailable
        return route(*args, **kwargs)

    return guarded
