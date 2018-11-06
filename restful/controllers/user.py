
import functools
import logging
from odoo import http
from odoo.http import request
from odoo.addons.restful.common import valid_response, invalid_response, extract_arguments
from odoo.addons.restful.controllers.main import validate_token


_logger = logging.getLogger(__name__)

class yogi_user(http.Controller):


    def __init__(self):
        self._model = 'ir.model'
        self.model = 'res.partner'

    _routes = [
        '/api/user',
        '/api/user/<id>',
        '/api/user/<id>/<action>'
    ]

  #  @validate_token
    @http.route(_routes, type='http', auth="none", methods=['GET'], csrf=False)
    def get(self, id=None, **payload):
       # model = 'res.partner'
        ioc_name = self.model
        model = request.env[self._model].sudo().search(
            [('model', '=', self.model)], limit=1)

        if model:
            if id:
                domain = [('id', '=', id)]
                fields = ['id', 'name']
                data = request.env[model.model].sudo().search_read(
                    domain=domain, fields=fields)
            else:
                domain, fields, offset, limit, order = extract_arguments(
                    payload)
                if not order:
                    order = 'id asc'
                if not fields:
                    fields = ['id', 'name']

                data = request.env[model.model].sudo().search_read(
                    domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        if data:
            return valid_response(data)
        else:
            return valid_response(data)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % ioc_name)

    @validate_token
    @http.route(_routes, type='http', auth="none", methods=['POST'], csrf=False)
    def create(self, id=None, **payload):

        ioc_name = self.model
        model = request.env[self._model].sudo().search(
            [('model', '=', self.model)], limit=1)
        if model:
            try:
                resource = request.env[model.model].sudo().create(payload)
            except Exception as e:
                return invalid_response('params', e)
            else:
                data = {'id': resource.id}
                if resource:
                    return valid_response(data)
                else:
                    return valid_response(data)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % ioc_name)

    @validate_token
    @http.route(_routes, type='http', auth="none", methods=['PUT'], csrf=False)
    def put(self,id=None, **payload):
        """."""
        try:
            _id = int(id)
        except Exception as e:
            return invalid_response('invalid object id', 'invalid literal %s for id with base ' % id)
        _model = request.env[self._model].sudo().search(
            [('model', '=', self.model)], limit=1)
        if not _model:
            return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model, 404)
        try:
            request.env[_model.model].sudo().browse(_id).write(payload)
        except Exception as e:
            return invalid_response('exception', e.name)
        else:
            return valid_response('update %s record with id %s successfully!' % (_model.model, _id))

    @validate_token
    @http.route(_routes, type='http', auth="none", methods=['DELETE'], csrf=False)
    def delete(self, id=None, **payload):
        """."""
        try:
            _id = int(id)
        except Exception as e:
            return invalid_response('invalid object id', 'invalid literal %s for id with base ' % id)
        try:
            record = request.env[self.model].sudo().search([('id', '=', _id)])
            if record:
                record.unlink()
            else:
                return invalid_response('missing_record', 'record object with id %s could not be found' % _id, 404)
        except Exception as e:
            return invalid_response('exception', e.name, 503)
        else:
            return valid_response('record %s has been successfully deleted' % record.id)
