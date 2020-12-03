from odoo import fields, models, api, _


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    new_date = fields.Datetime(string='Date', store=True)
    new_date2 = fields.Datetime(string='Date', compute='compute_date')
    date = fields.Datetime('Date', required=True, store=True)

    @api.depends('date', 'new_date')
    def compute_date(self):
        for item in self:
            if item.new_date:
                item.new_date2 = item.new_date
                item.date = item.new_date2
            else:
                if item.date:
                    item.new_date2 = item.date
                else:
                    item.new_date2 = False
