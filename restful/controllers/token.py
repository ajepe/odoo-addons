import json
import logging

import werkzeug.wrappers

from odoo import http
from odoo.addons.restful.common import get_request_access_token, invalid_response, valid_response
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import request

_logger = logging.getLogger(__name__)


class AccessToken(http.Controller):
    """."""

    @http.route("/api/auth/token", methods=["GET"], type="http", auth="none", csrf=False)
    def token(self, **post):
        """The token URL to be used for getting the access_token:

        Args:
            **post must contain login and password.

        Returns:
            returns https response code 404 if failed error message in the body in json format
            and status code 202 if successful with the access_token.

        Example::

            import requests

            data = {
                'login': 'admin',
                'password': 'admin',
                'db': 'mydatabase'
            }
            base_url = 'http://localhost:8069'
            req = requests.get(
                '{}/api/auth/token'.format(base_url), params=data)
            content = req.json()
            headers = {'Authorization': 'Bearer {}'.format(content['access_token'])}
        """
        _token = request.env["api.access_token"]
        params = ["db", "login", "password"]
        params = {key: post.get(key) for key in params if post.get(key)}
        db, username, password = (
            params.get("db"),
            params.get("login"),
            params.get("password"),
        )
        _credentials_includes_in_body = all([db, username, password])
        if not _credentials_includes_in_body:
            # The request post body is empty the credetials maybe passed via the headers.
            headers = request.httprequest.headers
            db = headers.get("db")
            username = headers.get("login")
            password = headers.get("password")
            _credentials_includes_in_headers = all([db, username, password])
            if not _credentials_includes_in_headers:
                # Empty 'db' or 'username' or 'password:
                return invalid_response(
                    "missing_credentials", "either of the following are missing [db, username, password]", 400,
                )
        # Login in odoo database:
        try:
            credential = {"login": username, "password": password, "type": "password"}
            request.session.authenticate(db, credential)
        except AccessDenied:
            return invalid_response("access_denied", "Login, password or db invalid", 401)
        except AccessError as aee:
            return invalid_response("access_error", "Error: %s" % aee, 403)
        except Exception as e:
            # Invalid database:
            info = "The database name is not valid {}".format((e))
            error = "invalid_database"
            _logger.error(info)
            return invalid_response("wrong database name", error, 400)

        uid = request.session.uid
        # odoo login failed:
        if not uid:
            info = "authentication failed"
            error = "authentication failed"
            _logger.error(info)
            return invalid_response(error, info, 401)

        # Generate tokens
        access_token = _token.find_one_or_create_token(user_id=uid, create=True)
        # Successful response:
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                {
                    "uid": uid,
                    "user_context": dict(request.session.context) if uid else {},
                    "company_id": request.env.user.company_id.id if uid else None,
                    "company_ids": request.env.user.company_ids.ids if uid else None,
                    "partner_id": request.env.user.partner_id.id,
                    "access_token": access_token,
                    "company_name": request.env.user.company_name,
                    "currency": request.env.user.company_id.currency_id.name,
                    "country": request.env.user.country_id.name,
                    "contact_address": request.env.user.contact_address,
                }
            ),
        )

    @http.route(["/api/auth/token"], methods=["DELETE"], type="http", auth="none", csrf=False)
    def delete(self, **post):
        """Delete a given token"""
        token = request.env["api.access_token"].sudo()
        access_token = get_request_access_token() or post.get("access_token")

        access_token = token.search([("token", "=", access_token)], limit=1)
        if not access_token:
            error = "Access token is missing in the request header or invalid token was provided"
            return invalid_response("missing_access_token", error, 400)
        for token in access_token:
            token.unlink()
        # Successful response:
        return valid_response([{"message": "access token %s successfully deleted" % (access_token,), "delete": True}])
