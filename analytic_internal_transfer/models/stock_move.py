from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
