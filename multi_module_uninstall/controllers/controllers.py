# -*- coding: utf-8 -*-
from odoo import http

# class MultiModuleUninstall(http.Controller):
#     @http.route('/multi_module_uninstall/multi_module_uninstall/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/multi_module_uninstall/multi_module_uninstall/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('multi_module_uninstall.listing', {
#             'root': '/multi_module_uninstall/multi_module_uninstall',
#             'objects': http.request.env['multi_module_uninstall.multi_module_uninstall'].search([]),
#         })

#     @http.route('/multi_module_uninstall/multi_module_uninstall/objects/<model("multi_module_uninstall.multi_module_uninstall"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('multi_module_uninstall.object', {
#             'object': obj
#         })