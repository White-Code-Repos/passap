from odoo import api, fields, models, _, SUPERUSER_ID
import odoo.addons.decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    resupply_id = fields.Many2one(comodel_name="stock.resupply.request", string="", required=False, )

    def action_cancel(self):
        res = super(StockPicking, self).action_cancel()
        if self.resupply_id:
            stock_request = self.env['stock.resupply.request'].search([('id', '=', self.resupply_id.id)])
            if stock_request.state!='rejected':
                stock_request.button_rejected()
            return res
        else:
            return res

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if self.resupply_id:
            stock_request = self.env['stock.resupply.request'].search([('id', '=', self.resupply_id.id)])
            if stock_request.state != 'done':
                stock_request.button_done()
            return res
        else:
            return res
