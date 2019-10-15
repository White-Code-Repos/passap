from odoo import models, fields, api
from datetime import datetime

class YearPlane(models.Model):
    _name = 'year.plan'
    state = fields.Selection([('draft', 'Draft'), ('ceoApp', 'To CEO Approve'),('approved','Approved')], string='Status',
                             required=True, readonly=True, copy=False, default='draft')
    name = fields.Char('Plan Name',required=True)
    year = fields.Selection([(num, str(num)) for num in range(1900, (datetime.now().year)+1 )], 'Year')
    responsible = fields.Many2one('res.partner','Responsible')
    plan_line_ids = fields.One2many('year.plan.month', 'plan_id')

    source = fields.Many2one('year.plan','Version Of',readonly=True)
#     Methods

    @api.multi
    def action_submit_plan(self):
        self.write({'state': 'ceoApp'})
    @api.multi
    def action_approve_plan(self):
        self.write({'state':'approved'})

    @api.multi
    def action_adjust_plan(self):
        versions = len(self.env['year.plan'].search([('source','=',self.id)]))
        list =[]
        for l in self.plan_line_ids:
            line = [0,0,{
                'analytic_account_id':l.analytic_account_id.id,
                'jan':l.jan,
                'feb':l.feb,
                'mar':l.mar,
                'apr':l.apr,
                'may':l.may,
                'june':l.june,
                'july':l.july,
                'aug':l.aug,
                'sept':l.sept,
                'oct':l.oct,
                'nov':l.nov,
                'dec':l.dec }]
            list.append(line)
        vals = {
            'state':'draft',
            'name':self.name+' version '+str(versions+1),
            'year':self.year,
            'responsible':self.responsible.id,
            'plan_line_ids':list,
            'source':self.id,
        }
        new_obj = self.env['year.plan'].create(vals)

    @api.multi
    def open_versions(self):
        plan_ids = self.env['year.plan'].search([('source','=',self.id)])
        list=[]
        for id in plan_ids:
            list.append(id)

        return {
            'name': 'Versions',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'year.plan',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', plan_ids.ids)],
        }

class YearPlaneMonth(models.Model):

    _name = 'year.plan.month'

    analytic_account_id = fields.Many2one('account.analytic.account','Analytic Account')
    jan = fields.Integer('Jan.')
    feb = fields.Integer('Feb.')
    mar = fields.Integer('Mar.')
    apr = fields.Integer('Apr.')
    may = fields.Integer('May')
    june = fields.Integer('June')
    july = fields.Integer('July')
    aug = fields.Integer('Aug.')
    sept = fields.Integer('Sept.')
    oct = fields.Integer('Oct.')
    nov = fields.Integer('Nov.')
    dec = fields.Integer('Dec.')
    total = fields.Integer('Total',compute='get_total')
    plan_id = fields.Many2one('year.plan')

    @api.multi
    def get_total(self):
        for rec in self:
            rec.total = rec.jan + rec.feb + rec.mar + rec.apr + rec.may + rec.june \
                    + rec.july + rec.aug + rec.sept + rec.oct + rec.nov + rec.dec





