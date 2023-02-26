# -*- coding: utf-8 -*-
# from odoo import http


# class Finalgalaxy(http.Controller):
#     @http.route('/finalgalaxy/finalgalaxy', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/finalgalaxy/finalgalaxy/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('finalgalaxy.listing', {
#             'root': '/finalgalaxy/finalgalaxy',
#             'objects': http.request.env['finalgalaxy.finalgalaxy'].search([]),
#         })

#     @http.route('/finalgalaxy/finalgalaxy/objects/<model("finalgalaxy.finalgalaxy"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('finalgalaxy.object', {
#             'object': obj
#         })
