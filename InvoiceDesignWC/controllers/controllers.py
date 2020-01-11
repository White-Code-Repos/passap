# -*- coding: utf-8 -*-
from odoo import http

# class Hospitalmodule(http.Controller):
#     @http.route('/hospitalmodule/hospitalmodule/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hospitalmodule/hospitalmodule/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hospitalmodule.listing', {
#             'root': '/hospitalmodule/hospitalmodule',
#             'objects': http.request.env['hospitalmodule.hospitalmodule'].search([]),
#         })

#     @http.route('/hospitalmodule/hospitalmodule/objects/<model("hospitalmodule.hospitalmodule"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hospitalmodule.object', {
#             'object': obj
#         })