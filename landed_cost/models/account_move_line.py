from odoo import fields,api,models,_
from odoo.exceptions import UserError, ValidationError

class ACCOUNTINVOICELINE(models.Model):
    _inherit = 'account.move.line'
    check_journal = fields.Boolean()
    product_id=fields.Many2one('product.product')
# class AccountMove(models.Model):
#     _inherit = "account.move"



    # @api.constrains('line_ids', 'journal_id', 'auto_reverse', 'reverse_date')
    # def _validate_move_modification(self):
    #
    #     if 'posted' in self.mapped('line_ids.payment_id.state') and False in self.mapped('line_ids.payment_id.check_payment'):
    #             raise ValidationError(_("You cannot modify a journal entry linked to a posted payment."))

