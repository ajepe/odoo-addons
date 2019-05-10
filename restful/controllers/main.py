"""Part of odoo. See LICENSE file for full copyright and licensing details."""

import functools
import logging
from odoo import http
from odoo.http import request
from odoo.addons.restful.common import valid_response, invalid_response, prepare_response, extract_arguments

_logger = logging.getLogger(__name__)

def validate_token(func):
    """."""
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = request.httprequest.headers.get('access_token')
        if not access_token:
            return invalid_response('access_token_not_found', 'missing access token in request header', 401)

        access_token_data = request.env['api.access_token'].sudo().search(
            [('token', '=', access_token)], order='id DESC', limit=1)

        if access_token_data.find_one_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_response('access_token', 'token seems to have expired or invalid', 401)

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)
    return wrap

def validate_id(func):
    """."""
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        id = kwargs['id']
        try:
            kwargs['id'] = int(id)
        except Exception as e:
            return invalid_response('invalid object id', 'invalid id %s' % id)
        else:
            return func(self, *args, **kwargs)
    return wrap

def validate_model(func):
    """."""
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        model = kwargs['model']
        _model = request.env['ir.model'].sudo().search(
            [('model', '=', model)], limit=1)
        if not _model:
            return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model, 404)
        return func(self, *args, **kwargs)
    return wrap

class APIController(http.Controller):
    """."""

    @validate_token
    @validate_id
    @validate_model
    @http.route('/api/<model>/<id>', type='http', auth="none", methods=['GET'], csrf=False)
    def get(self, model=None, id=None):
        """Get record by id.
        Basic usage:
        import requests

        headers = {
            'charset': 'utf-8',
            'access-token': 'access_token'
        }
        model = 'res.partner'
        id = 100
        req = requests.get('{}/api/{}/{}'.format(base_url, model, id), headers=headers)
        print(req.json())
        """
        try:
            record = request.env[model].sudo().browse(id)
            if record.read():
                return valid_response(prepare_response(record.read(), one=True))
            else:
                return invalid_response('missing_record',
                                        'record object with id %s could not be found' % (id, model), 404)
        except Exception as e:
            return invalid_response('exception', str(e))

    @validate_token
    @validate_model
    @http.route('/api/<model>', type='http', auth="none", methods=['GET'], csrf=False)
    def search(self, model=None, **kwargs):
        """Get records by search query.
        Basic usage:
        import requests

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8',
            'access-token': 'access_token'
        }
        model = 'res.partner'
        data = {
            'domain': "[('supplier','=',True),('parent_id','=', False)]",
            'order': 'name asc',
            'limit': 10,
            'offset': 0,
            'fields': "['name', 'supplier', 'parent_id']"
        }
        ###
        #You can ommit unnessesary query params
        #data = {
        #    'domain': "[('supplier','=',True),('parent_id','=', False)]",
        #    'limit': 10
        #}
        ###
        #You can also use JSON-like domains
        #data = {
        #    'domain': "{'id':100, 'parent_id!':true}",
        #    'limit': 10
        #}
        req = requests.get('{}/api/{}/'.format(base_url, model), headers=headers, params=data)
        print(req.json())
        """
        domain, fields, offset, limit, order = extract_arguments(kwargs)
        data = request.env[model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        return valid_response(prepare_response(data))

    @validate_token
    @validate_model
    @http.route('/api/<model>', type='http', auth="none", methods=['POST'], csrf=False)
    def create(self, model=None, **kwargs):
        """Create a new record.
        Basic usage:
        import requests

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8',
            'access-token': 'access_token'
        }
        model = 'res.partner'
        data = {
            'name': 'Babatope Ajepe',
            'country_id': 105,
            'child_ids': [
                {
                    'name': 'Contact',
                    'type': 'contact'
                },
                {
                    'name': 'Invoice',
                    'type': 'invoice'
                }
            ],
            'category_id': [{'id': 9}, {'id': 10}]
        }
        req = requests.post('{}/api/{}/'.format(base_url, model), headers=headers, data=data)
        print(req.json())
        """

        try:
            record = request.env[model].sudo().create(kwargs)
            record.refresh()
            return valid_response(prepare_response(record.read(), one=True))
        except Exception as e:
            return invalid_response('params', e)


    @validate_token
    @validate_id
    @validate_model
    @http.route('/api/<model>/<id>', type='http', auth="none", methods=['PUT'], csrf=False)
    def put(self, model=None, id=None, **kwargs):
        """Update existing record.
        Basic usage:
        import requests

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8',
            'access-token': 'access_token'
        }
        model = 'res.partner'
        id = 100
        data = {
            'name': 'Babatope Ajepe',
            'country_id': 103,
            'category_id': [{'id': 9}]
        }
        req = requests.put('{}/api/{}/{}'.format(base_url, model, id), headers=headers, data=data)
        print(req.json())
        """

        try:
            record = request.env[model].sudo().browse(id)
            if record.read():
                result = record.write(kwargs)
                record.refresh()
                return valid_response(prepare_response(record.read(), one=True))
            else:
                return invalid_response('missing_record', 'record object with id %s could not be found' % id, 404)
        except Exception as e:
            return invalid_response('exception', str(e))

    @validate_token
    @validate_id
    @validate_model
    @http.route('/api/<model>/<id>/<action>', type='http', auth="none", methods=['PATCH'], csrf=False)
    def patch(self, model=None, id=None, action=None, **kwargs):
        """Call action for model.
        Basic usage:
        import requests

        headers = {
            'charset': 'utf-8',
            'access-token': 'access_token'
        }
        model = 'res.partner'
        id = 100
        action = 'delete'
        req = requests.patch('{}/api/res.{}/{}'.format(base_url, model, id, action), headers=headers)
        print(req.content)
        """

        try:
            record = request.env[model].sudo().browse(id)
            if record.read():
                _callable = action in [method for method in dir(
                    record) if callable(getattr(record, method))]
                if _callable:
                    # action is a dynamic variable.
                    getattr(record, action)()
                record.refresh()
                return valid_response(prepare_response(record.read(), one=True))
            else:
                return invalid_response('missing_record',
                                        'record object with id %s could not be found or %s object has no method %s' % (id, model, action), 404)
        except Exception as e:
            return invalid_response('exception', e, 503)

    @validate_token
    @validate_id
    @validate_model
    @http.route('/api/<model>/<id>', type='http', auth="none", methods=['DELETE'], csrf=False)
    def delete(self, model=None, id=None):
        """Delete existing record.
        Basic usage:
        import requests

        headers = {
            'charset': 'utf-8',
            'access-token': 'access_token'
        }
        model = 'res.partner'
        id = 100
        req = requests.delete('{}/api/{}/{}'.format(base_url, model, id), headers=headers)
        print(req.json())
        """

        try:
            record = request.env[model].sudo().browse(id)
            if record.read():
                record.unlink()
                return valid_response(None, status=204)
            else:
                return invalid_response('missing_record', 'record object with id %s could not be found' % id, 404)
        except Exception as e:
            return invalid_response('exception', str(e), 503)

