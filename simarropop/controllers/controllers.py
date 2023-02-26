# -*- coding: utf-8 -*-
# from odoo import http


# class Simarropop(http.Controller):
#     @http.route('/simarropop/simarropop', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/simarropop/simarropop/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('simarropop.listing', {
#             'root': '/simarropop/simarropop',
#             'objects': http.request.env['simarropop.simarropop'].search([]),
#         })

#     @http.route('/simarropop/simarropop/objects/<model("simarropop.simarropop"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('simarropop.object', {
#             'object': obj
#         })
