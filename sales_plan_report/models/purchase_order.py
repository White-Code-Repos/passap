from odoo import api, fields, models



class purchase_order(models.Model):
    _inherit = 'purchase.order'

    egp_rate = fields.Float(string="EGP Rate",  required=False, )
    egp_total = fields.Float(string="EGP Total Amount",  required=False, )

    @api.onchange('egp_rate','amount_total')
    def onchange_calc_egp(self):
        self.egp_total = self.egp_rate*self.amount_total

    @api.constrains('egp_rate', 'amount_total')
    def constrains_calc_egp(self):
        self.egp_total = self.egp_rate * self.amount_total


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    # egp_rate = fields.Float(string="EGP Rate",readonly=True,  required=False, )
    egp_total_total = fields.Float(string="EGP Total",related='purchase_id.egp_total',  required=False, )

