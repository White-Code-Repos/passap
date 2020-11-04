from odoo import models, fields, api

class crossovered_budget(models.Model):
    _inherit = 'crossovered.budget.lines'

    difference = fields.Float('Difference',store=True,force_save=True)
    # account_ids=fields.Many2many('account.account',compute='get_budgets')

    account_id = fields.Many2one('account.account')

    @api.onchange('planned_amount','practical_amount')
    def get_amount_difference(self):

        for item in self:
            item.difference=item.planned_amount - item.practical_amount

    @api.onchange('general_budget_id')
    def get_budgets(self):
        list=[]
        for item in self:
           budget_id=self.env['account.budget.post'].search([('id','=',item.general_budget_id.id)])
           for budget in budget_id:
               for account in budget.account_ids:
                   list.append(account.id)
           domain = [('id', 'in', list)]
           return {'domain': {'account_id': domain}}



