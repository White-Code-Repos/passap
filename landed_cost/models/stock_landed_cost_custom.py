from odoo import fields,api,models,_
from odoo.exceptions import UserError, ValidationError

class STOCKLANDEDCOSTCUSTOM(models.Model):
    _inherit = 'product.product'
    income_terms = fields.Many2many('account.incoterms', string='Income Term' )




