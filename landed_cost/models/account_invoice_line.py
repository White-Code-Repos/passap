from odoo import fields,api,models,_
from odoo.exceptions import UserError, ValidationError

class ACCOUNTINVOICELINE(models.Model):
    _inherit = 'account.invoice.line'
    custom_percent=fields.Float()
    non_custom_percent=fields.Float(store=True,readonly=True,force_save=True)

class ACCOUNTINVOICE(models.Model):
    _inherit = "account.invoice"
    @api.onchange('invoice_line_ids')
    def get_non_custom_percent(self):
        total_quantity=0
        for item in self:
            for rec in item.invoice_line_ids:
                total_quantity+=rec.quantity
            for line in item.invoice_line_ids:
                if total_quantity > 0:
                    line.non_custom_percent = line.quantity / total_quantity

class ACCOUNTAcount(models.Model):
    _inherit = "account.account"
    lc_account=fields.Boolean()
class ACCOUNTJournal(models.Model):
    _inherit = "account.journal"
    lc_account=fields.Boolean()
