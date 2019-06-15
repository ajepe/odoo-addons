"""Common methods"""
import ast
import logging

import werkzeug.wrappers

from odoo.http import request

_logger = logging.getLogger(__name__)
try:
    import simplejson as json
    from simplejson.errors import JSONDecodeError
except ModuleNotFoundError as identifier:
    _logger.error(identifier)
else:
    import json


def valid_response(data, status=200):
    """Valid Response
    This will be return when the http request was successfully processed."""
    data = {"count": len(data), "data": data}
    return werkzeug.wrappers.Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(data),
    )


def invalid_response(typ, message=None, status=401):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server."""
    # return json.dumps({})
    return werkzeug.wrappers.Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(
            {
                "type": typ,
                "message": str(message)
                if str(message)
                else "wrong arguments (missing validation)",
            }
        ),
    )


def extract_arguments(payloads, offset=0, limit=0, order=None):
    """."""
    fields, domain, payload = [], [], {}
    data = str(payloads)[2:-2]
    try:
        payload = json.loads(data)
    except JSONDecodeError as e:
        _logger.error(e)
    if payload.get("domain"):
        for _domain in payload.get("domain"):
            l, o, r = _domain
            if o == "': '":
                o = "="
            elif o == "!': '":
                o = "!="
            domain.append(tuple([l, o, r]))
    if payload.get("fields"):
        fields += payload.get("fields")
    if payload.get("offset"):
        offset = int(payload["offset"])
    if payload.get("limit"):
        limit = int(payload.get("limit"))
    if payload.get("order"):
        order = payload.get("order")
    return [domain, fields, offset, limit, order]
