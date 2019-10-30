
from odoo import fields, models, api

class ResPartnerChange(models.Model) :
    _inherit = 'res.partner'

    commercial_register = fields.Char('Commercial Register')
    industrial_register = fields.Char('Industrial Register')
    value_reg_certificate = fields.Char('Value Added Registration Certificate')
    exempt_non = fields.Char('Exempt or non-exempt')
    exp = fields.Integer('EXP industrial register')
    file_tax = fields.Char('Tax File')