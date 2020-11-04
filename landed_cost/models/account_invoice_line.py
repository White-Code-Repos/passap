from odoo import fields,api,models,_
from odoo.exceptions import UserError, ValidationError

class ACCOUNTINVOICELINE(models.Model):
    _inherit = 'account.invoice.line'
    custom_percent=fields.Float()
    non_custom_percent=fields.Float(store=True,readonly=True,force_save=True)

class ACCOUNTINVOICE(models.Model):
    _inherit = "account.invoice"
    custom_total_dolar=fields.Float()
    custom_total_egp=fields.Float()


    @api.onchange('invoice_line_ids')
    def get_non_custom_percent(self):
        total_quantity=0
        total_custom=0
        custom_amount=0
        currency_id=self.env['res.currency'].search([('name','=','USD')])
        print(currency_id.rate)
        print(currency_id.name)
        for item in self:
            for rec in item.invoice_line_ids:
                total_quantity+=rec.quantity
                total_custom +=rec.custom_percent
                custom_amount +=(rec.custom_percent/100)*rec.price_subtotal
                for rec in item.invoice_line_ids:
                    if total_quantity > 0:
                        rec.non_custom_percent = rec.quantity / total_quantity
            item.custom_total_dolar=custom_amount
            item.custom_total_egp=custom_amount/currency_id.rate
                    # if total_custom > 100:
                    #     raise UserError(
                    #         _('Sorry total of  custom percentage must be small than 100% re arrange the custom percentage in the invoice line'))



class ACCOUNTAcount(models.Model):
    _inherit = "account.account"
    lc_account=fields.Boolean()
