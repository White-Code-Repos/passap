from odoo import fields,api,models,_
from odoo.exceptions import UserError, ValidationError

class LANDEDCOST(models.Model):
    _inherit = 'account.payment'
    lc_expense_name=fields.Many2one('stock.landed.cost',string="LC Expense Name")
    lc_expense_id = fields.Many2one('product.product', string="LC Expense Name")
    payment_type = fields.Selection(selection_add=[('expense', 'LC Expense'),('payment', 'LC payment')])
    letter_of_credit_id=fields.Many2one('letter.credit')








