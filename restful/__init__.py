from . import common, controllers, models

import re
import odoo
import logging
import werkzeug
from odoo.http import HttpRequest, Root, SessionExpiredException, request,Response
import json
from odoo.http import JsonRequest, WebRequest

from odoo.service import security, model as service_model

_handle_exception = JsonRequest._handle_exception  # original json _handle_exception method


def request_restful(httprequest, **kwargs):
    """Proxy request to the actual destination."""
    c = controllers.main.APIController()
    path = httprequest.path
    _id = re.findall(r"\d+", path)
    _id = int(_id[0]) if _id else False
    path = path.split("/")
    model = path[2]
    return getattr(c, httprequest.method.lower())(model=model, id=_id, payload=kwargs)


_logger = logging.getLogger(__name__)


def _handle_exception(self, exception):
    """Called within an except block to allow converting exceptions
           to arbitrary responses. Anything returned (except None) will
           be used as response."""
    if self.httprequest.headers.get("access-token", False):
        return request_restful(
            self.httprequest, **json.loads(self.httprequest.get_data().decode(self.httprequest.charset))
        )
    try:
        return super(JsonRequest, self)._handle_exception(exception)
    except Exception:
        if not isinstance(
            exception,
            (
                odoo.exceptions.Warning,
                SessionExpiredException,
                odoo.exceptions.except_orm,
                werkzeug.exceptions.NotFound,
            ),
        ):
            _logger.exception("Exception during JSON request handling.")
        error = {
            "code": 200,
            "message": "Odoo Server Error",
            # 'data': serialize_exception(exception)
        }

        return self._json_response(error=error)


def _call_function(self, *args, **kwargs):
    request = self

    if self.endpoint.routing["type"] != self._request_type:
        token = self.httprequest.headers.get("access-token", False)

        if not token:
            msg = "%s, %s: Function declared as capable of handling request of type '%s' but called with a request of type '%s'"
            params = (self.endpoint.original, self.httprequest.path, self.endpoint.routing["type"], self._request_type)
            _logger.info(msg, *params)
            raise werkzeug.exceptions.BadRequest(msg % params)

    if self.endpoint_arguments:
        kwargs.update(self.endpoint_arguments)

    # Backward for 7.0
    if self.endpoint.first_arg_is_req:
        args = (request,) + args

    # Correct exception handling and concurency retry
    @service_model.check
    def checked_call(___dbname, *a, **kw):
        # The decorator can call us more than once if there is an database error. In this
        # case, the request cursor is unusable. Rollback transaction to create a new one.
        if self._cr:
            self._cr.rollback()
            self.env.clear()
        result = self.endpoint(*a, **kw)
        if isinstance(result, Response) and result.is_qweb:
            # Early rendering of lazy responses to benefit from @service_model.check protection
            result.flatten()
        return result

    if self.db:
        return checked_call(self.db, *args, **kwargs)
    return self.endpoint(*args, **kwargs)


JsonRequest._handle_exception = _handle_exception
# WebRequest._call_function = _call_function
