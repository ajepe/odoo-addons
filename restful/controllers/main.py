import ast
import functools
import json
import logging

from odoo import http
from odoo.addons.restful.common import (
    extract_arguments,
    get_request_access_token,
    invalid_response,
    valid_response,
)
from odoo.exceptions import AccessError
from odoo.http import request

_logger = logging.getLogger(__name__)


def validate_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = get_request_access_token()
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)
        access_token_data = (
            request.env["api.access_token"].sudo().search([("token", "=", access_token)], order="id DESC", limit=1)
        )

        if access_token_data.find_one_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_response("access_token", "token seems to have expired or invalid", 401)

        request.update_env(user=access_token_data.user_id.id)
        return func(self, *args, **kwargs)

    return wrap


_routes = ["/api/<model>", "/api/<model>/<id>", "/api/<model>/<id>/<action>"]


class APIController(http.Controller):
    """."""

    def __init__(self):
        self._model = "ir.model"

    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["GET"], csrf=False)
    def get(self, model=None, id=None, **payload):
        try:
            domain, fields, offset, limit, order = extract_arguments(**payload)
        except (ValueError, TypeError) as e:
            return invalid_response("invalid_arguments", "Error: %s" % e, 400)
        ioc_name = model
        # ir.model is only readable by group_erp_manager in Odoo 18,
        # the metadata lookup is done as superuser but the data is
        # read with the token user's access rights and record rules.
        model = request.env[self._model].sudo().search([("model", "=", model)], limit=1)
        if not model:
            return invalid_response(
                "invalid object model", "The model %s is not available in the registry." % ioc_name, 404,
            )
        if id:
            try:
                _id = int(id)
            except (ValueError, TypeError):
                return invalid_response("invalid object id", "invalid literal %s for id" % id, 400)
            domain = [("id", "=", _id)]
        try:
            data = request.env[model.model].search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order,
            )
        except AccessError as e:
            return invalid_response("access_error", "Error: %s" % e, 403)
        except Exception as e:
            return invalid_response("invalid_arguments", "Error: %s" % e, 400)
        return valid_response(data)

    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["POST"], csrf=False)
    def post(self, model=None, id=None, **payload):
        """Create a new record.

        Basic usage::

            import requests

            headers = {
                'content-type': 'application/json',
                'Authorization': 'Bearer access_token_xxx'
            }
            data = {
                'partner_id': 10,
                'order_line': [(0, 0, {'product_id': 1, 'price_unit': 4000})],
            }
            req = requests.post('%s/api/sale.order' % base_url,
                                headers=headers, data=json.dumps(data))

        x2many fields accept Odoo command lists as native JSON arrays under
        the plain field name.
        """
        fields = payload.get("fields")
        if not fields:
            fields = []
        else:
            fields = fields.split(",")
        try:
            payload = json.loads(request.httprequest.data.decode() or "{}")
        except ValueError as e:
            return invalid_response("invalid_json", "Error: %s" % e, 400)
        ioc_name = model
        model = request.env[self._model].sudo().search([("model", "=", model)], limit=1)
        if not model:
            return invalid_response(
                "invalid object model", "The model %s is not available in the registry." % ioc_name, 404,
            )
        try:
            resource = request.env[model.model].create(payload)
        except AccessError as e:
            request.env.cr.rollback()
            return invalid_response("access_error", "Error: %s" % e, 403)
        except Exception as e:
            request.env.cr.rollback()
            return invalid_response("params", e, 400)
        else:
            data = resource.read(fields=fields)
            return valid_response(data, 201)

    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["PUT"], csrf=False)
    def put(self, model=None, id=None, **payload):
        """."""
        try:
            payload = json.loads(request.httprequest.data.decode() or "{}")
        except ValueError as e:
            return invalid_response("invalid_json", "Error: %s" % e, 400)
        try:
            _id = int(id)
        except (ValueError, TypeError):
            return invalid_response("invalid object id", "invalid literal %s for id" % id, 400)
        _model = request.env[self._model].sudo().search([("model", "=", model)], limit=1)
        if not _model:
            return invalid_response(
                "invalid object model", "The model %s is not available in the registry." % model, 404,
            )
        record = request.env[_model.model].browse(_id)
        if not record.exists():
            return invalid_response("missing_record", "record object with id %s could not be found" % _id, 404)
        try:
            record.write(payload)
        except AccessError as e:
            request.env.cr.rollback()
            return invalid_response("access_error", "Error: %s" % e, 403)
        except Exception as e:
            request.env.cr.rollback()
            return invalid_response("exception", e, 400)
        else:
            return valid_response(record.read())

    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["DELETE"], csrf=False)
    def delete(self, model=None, id=None, **payload):
        """."""
        try:
            _id = int(id)
        except (ValueError, TypeError):
            return invalid_response("invalid object id", "invalid literal %s for id" % id, 400)
        if model not in request.env:
            return invalid_response(
                "invalid object model", "The model %s is not available in the registry." % model, 404,
            )
        record = request.env[model].search([("id", "=", _id)])
        if not record:
            return invalid_response("missing_record", "record object with id %s could not be found" % _id, 404)
        try:
            record.unlink()
        except AccessError as e:
            request.env.cr.rollback()
            return invalid_response("access_error", "Error: %s" % e, 403)
        except Exception as e:
            request.env.cr.rollback()
            return invalid_response("exception", e, 400)
        else:
            return valid_response("record %s has been successfully deleted" % record.id)

    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["PATCH"], csrf=False)
    def patch(self, model=None, id=None, action=None, **payload):
        """."""
        payload_str = request.httprequest.data.decode()
        try:
            args = ast.literal_eval(payload_str) if payload_str else []
        except (ValueError, SyntaxError) as e:
            return invalid_response("invalid_arguments", "Error: %s" % e, 400)
        if not isinstance(args, (list, tuple)):
            return invalid_response("invalid_arguments", "PATCH body must be a list of arguments", 400)
        try:
            _id = int(id)
        except (ValueError, TypeError):
            return invalid_response("invalid object id", "invalid literal %s for id" % id, 400)
        if model not in request.env:
            return invalid_response(
                "invalid object model", "The model %s is not available in the registry." % model, 404,
            )
        record = request.env[model].search([("id", "=", _id)], limit=1)
        _callable = action in [method for method in dir(record) if callable(getattr(record, method))]
        if not record or not _callable:
            return invalid_response(
                "invalid object or method",
                "The given action '%s ' cannot be performed on record with id '%s' because '%s' has no such method"
                % (action, _id, model),
                404,
            )
        try:
            # action is a dynamic variable.
            res = getattr(record, action)(*args) if args else getattr(record, action)()
        except AccessError as e:
            request.env.cr.rollback()
            return invalid_response("access_error", "Error: %s" % e, 403)
        except Exception as e:
            request.env.cr.rollback()
            return invalid_response("exception", e, 400)
        else:
            return valid_response(res)
