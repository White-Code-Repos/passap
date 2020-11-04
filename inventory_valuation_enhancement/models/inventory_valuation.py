from odoo import api, fields, models, tools


class StockValuation(models.Model):
    _inherit = 'product.product'

    location_id = fields.Many2one(comodel_name='stock.location', string='Location', compute='get_location')

    def get_location(self):
        for item in self:
            stock = item.env['stock.quant'].search([('product_id', '=', item.id)])
            for sto in stock:
                item.location_id = sto.location_id.id
