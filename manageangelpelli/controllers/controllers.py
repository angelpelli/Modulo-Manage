# -*- coding: utf-8 -*-
# from odoo import http


# class Manageangelpelli(http.Controller):
#     @http.route('/manageangelpelli/manageangelpelli', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/manageangelpelli/manageangelpelli/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('manageangelpelli.listing', {
#             'root': '/manageangelpelli/manageangelpelli',
#             'objects': http.request.env['manageangelpelli.manageangelpelli'].search([]),
#         })

#     @http.route('/manageangelpelli/manageangelpelli/objects/<model("manageangelpelli.manageangelpelli"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('manageangelpelli.object', {
#             'object': obj
#         })
