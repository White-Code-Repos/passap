# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_confirm(self):
        super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.order_line:
                for line in order.order_line:
                    line.product_id.last_purchase_price = line.price_unit
        return True
