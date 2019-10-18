from odoo import models, fields, api

class purchase_requestion(models.Model):
    _inherit = 'material.purchase.requisition'

    type = fields.Char('Requisition Type')
