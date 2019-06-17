# Part of odoo. See LICENSE file for full copyright and licensing details.
import logging
import json
import werkzeug.wrappers
from odoo import http
from odoo.http import request
from odoo.addons.restful.common import invalid_response, token_response, valid_response

_logger = logging.getLogger(__name__)

expires_in = 'restful.access_token_expires_in'

class AccessToken(http.Controller):
    """."""

    @http.route('/api/auth/token', methods=['POST'], type='http', auth='none', csrf=False)
    def token(self, **kwargs):
        """The token URL to be used for getting the access_token:

        Args:
            **post must contain login and password.
        Returns:

            returns https response code 404 if failed error message in the body in json format
            and status code 202 if successful with the access_token.
        Example:
           import requests

           headers = {'content-type': 'text/plain', 'charset':'utf-8'}

           data = {
               'login': 'admin',
               'password': 'admin',
               'db': 'galago.ng'
            }
           base_url = 'http://odoo.ng'
           req = requests.post(
               '{}/api/auth/token'.format(base_url), data=data, headers=headers)
           content = json.loads(req.content.decode('utf-8'))
           headers.update(access-token=content.get('access_token'))
        """

        try:
            db, username, password = kwargs['db'], kwargs['login'], kwargs['password']
        except Exception as e:
            # Invalid database:
            error = 'missing'
            info = 'either of the following are missing [db, username,password]'
            status = 403
            _logger.error(info)
            return invalid_response(error, info, status)

        # Login in odoo database:
        try:
            request.session.authenticate(db, username, password)
        except Exception as e:
            # Invalid database:
            error = 'invalid_database'
            info = "The database name is not valid {}".format((e))
            _logger.error(info)
            return invalid_response(error, info)

        uid = request.session.uid

        # odoo login failed:
        if not uid:
            error = 'authentication failed'
            info = 'authentication failed'
            _logger.error(info)
            return invalid_response(error, info)

        # Generate tokens
        access_token = request.env['api.access_token'].sudo().find_one_or_create_token(
            user_id=uid, create=True)

        # Successful response:
        return token_response({
            'uid': uid,
            'user_context': request.session.get_context(),
            'company_id': request.env.user.company_id.id,
            'access_token': access_token,
            'expires_in': request.env.ref(expires_in).sudo().value,
        })

    @http.route('/api/auth/token', methods=['DELETE'], type='http', auth='none', csrf=False)
    def delete(self, **kwargs):
        """."""
        request_token = request.httprequest.headers.get('access_token')
        access_token  = request.env['api.access_token'].sudo().search([('token', '=', request_token)])
        if not access_token:
            error = 'no_access_token'
            info = 'No access token was provided in request!'
            _logger.error(info)
            return invalid_response(error, info, 400)

        for token in access_token:
            token.unlink()

        # Successful response:
        return valid_response({
            'desc': 'token successfully deleted',
            'delete': True
        })
