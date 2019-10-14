# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    last_purchase_price = fields.Float(string='Last Purchase Price', readonly=True)