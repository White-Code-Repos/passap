# -*- coding: utf-8 -*-

from odoo import models, fields, api

class VendorEvaluationCT(models.Model):
    _name = 'vendor.evaluation'
    _rec_name = 'order_number'

    order_number = fields.Char()
    quality_delivery = fields.Char(string='Quality Delivery')
    delivery_date = fields.Date(string='Delivery Date')
    quantity_delivery = fields.Float(string='Quantity Delivery')
    price = fields.Float(string='Price')