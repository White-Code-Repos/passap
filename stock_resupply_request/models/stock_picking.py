from odoo import api, fields, models, _ , SUPERUSER_ID
import odoo.addons.decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    def action_cancel(self):
        res = super(StockPicking,self).action_cancel()
        stock_request = self.env['stock.resupply.request'].search([('name','=',self.origin)])
        if stock_request:
            stock_request.button_rejected()

    def action_validate(self):
        res = super(StockPicking,self).action_validate()
        stock_request = self.env['stock.resupply.request'].search([('name','=',self.origin)])
        if stock_request:
            stock_request.button_done()