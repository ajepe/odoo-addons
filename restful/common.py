import datetime
import json
import logging

import werkzeug.wrappers

from odoo.http import request

_logger = logging.getLogger(__name__)


def get_request_access_token():
    """Extract the API access token from the current request.

    Supported transports (in order of precedence):
    - ``access_token`` header: legacy, silently dropped by most WSGI
      servers/proxies (werkzeug, nginx) because of the underscore.
    - ``access-token`` header: hyphenated variant of the above.
    - ``Authorization: Bearer <token>`` header: the standard scheme.
    """
    headers = request.httprequest.headers
    access_token = headers.get("access_token") or headers.get("access-token")
    if not access_token:
        auth_header = headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            access_token = auth_header[7:].strip()
    return access_token


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    if isinstance(o, bytes):
        return str(o)


def valid_response(data, status=200):
    """Valid Response
    This will be return when the http request was successfully processed."""
    data = {"count": len(data) if not isinstance(data, (int, str, bool, type(None))) else 1, "data": data}
    return werkzeug.wrappers.Response(
        status=status, content_type="application/json; charset=utf-8", response=json.dumps(data, default=default),
    )


def invalid_response(typ, message=None, status=400):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server."""
    return werkzeug.wrappers.Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(
            {"type": typ, "message": str(message) if str(message) else "wrong arguments (missing validation)",},
            default=datetime.datetime.isoformat,
        ),
    )


def extract_arguments(limit="80", offset=0, order="id", domain="", fields=None):
    """Parse additional data  sent along request."""
    limit = int(limit)
    expresions = []
    if domain:
        expresions = [tuple(preg.replace(":", ",").split(",")) for preg in domain.split(",")]
        expresions = json.dumps(expresions)
        expresions = json.loads(expresions, parse_int=True)
    if fields:
        fields = fields.split(",")

    if offset:
        offset = int(offset)
    return [expresions, fields, offset, limit, order]
