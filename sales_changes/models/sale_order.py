from odoo import models, fields, api
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'



    def _get_total_discount(self):
        discount = 0
        for line in self.order_line:
            discount += (line.discount/100)*line.price_unit
        self.total_discount = discount


    total_discount = fields.Monetary(string='Total Discount',compute='_get_total_discount')

class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    bom = fields.Many2many('mrp.bom',string='Bill Of Materials')

    @api.multi
    @api.onchange('product_id')
    def calc_bom(self):
        if self.product_id:
            product = self.env['product.template'].search([('name', '=', self.product_id.name)])
            boms = self.env['mrp.bom'].search([('product_tmpl_id', '=', product.id)])
            self.bom = [(6, 0, [v.id for v in boms])]

