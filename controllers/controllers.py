# -*- coding: utf-8 -*-
from odoo import http

# class TiendoSmartpurchase(http.Controller):
#     @http.route('/tiendo_smartpurchase/tiendo_smartpurchase/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tiendo_smartpurchase/tiendo_smartpurchase/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tiendo_smartpurchase.listing', {
#             'root': '/tiendo_smartpurchase/tiendo_smartpurchase',
#             'objects': http.request.env['tiendo_smartpurchase.tiendo_smartpurchase'].search([]),
#         })

#     @http.route('/tiendo_smartpurchase/tiendo_smartpurchase/objects/<model("tiendo_smartpurchase.tiendo_smartpurchase"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tiendo_smartpurchase.object', {
#             'object': obj
#         })