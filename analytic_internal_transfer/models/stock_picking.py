from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def get_account_analytic(self):
        moves = self.env['account.move'].search([('ref', '=', self.name)])
        total_debit = 0
        for move in self.move_ids_without_package:
            for m in moves:
                m.update({'state': 'draft'})
                for line in m.line_ids:
                    if line.debit != 0:
                        total_debit += line.debit
                        line.update({'analytic_account_id': move.account_analytic_id.id})
        return

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        self.get_account_analytic()
        return res

    @api.multi
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        self.get_account_analytic()
        return res
