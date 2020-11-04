from odoo import models, fields, api
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'product.product'
    location_idd = fields.Many2one('stock.location', 'Location',store=True)