from odoo import models, fields, api
from datetime import datetime

class MonthPlane(models.Model):
    _name = 'month.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([('draft', 'Draft'), ('mangerApp', 'To Manager Approve'), ('approved', 'Approved')],
                             string='Status',
                             required=True, readonly=True, copy=True, default='draft',track_visibility="onchange")
    name = fields.Char('Plan Name',required=True ,track_visibility="always")

    yearly_plan = fields.Many2one('year.plan','Yearly Plan' ,required=True,track_visibility="onchange",copy=True)
    month = fields.Selection([('jan','Jan'),
                              ('feb','Feb'),
                              ('mar','Mar'),
                              ('apr','Apr'),
                              ('may','May'),
                              ('june','June'),
                              ('july','July'),
                              ('aug','Aug'),
                              ('sept','Sept'),
                              ('oct','Oct'),
                              ('nov','Nov'),
                              ('dec','Dec')] ,'Month',required=True ,track_visibility="onchange",copy=True)
    source = fields.Many2one('month.plan','Version Of',readonly=True,copy=True)
    plan_m_line_ids = fields.One2many('month.plan.line', 'month_plan_id',copy=True)
    
    version_count = fields.Integer(compute='calc_values',copy=True)

    # Methods

    @api.multi
    def action_submit_plan(self):
        self.write({'state': 'mangerApp'})
    @api.multi
    def action_approve_plan(self):
        self.write({'state':'approved'})

    @api.multi
    def action_adjust_plan(self):
        versions = len(self.env['month.plan'].search([('source','=',self.id)]))
        list = []
        for l in self.plan_m_line_ids:
            line = [0, 0, {
                'business_line': l.business_line.id,
                'quantity': l.quantity,
                'product_id': l.product_id.id,
                'qty': l.qty,
            }]
            list.append(line)
        vals = {
            'state': 'draft',
            'name': self.name + ' version ' + str(versions + 1),
            'yearly_plan': self.yearly_plan.id,
            'month': self.month,
            'plan_m_line_ids': list,
            'source': self.id,
        }
        new_obj = self.env['month.plan'].create(vals)

    @api.multi
    def open_versions(self):
            plan_ids = self.env['month.plan'].search([('source', '=', self.id)])
            list = []
            for id in plan_ids:
                list.append(id)

            return {
                'name': 'Versions',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'month.plan',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', plan_ids.ids)],
            }

    @api.multi
    def calc_values(self):
        for obj in self:
            obj.version_count = len(self.env['month.plan'].search([('source', '=', obj.id)]))


class MonthPlaneLine(models.Model):
    _name = 'month.plan.line'

    business_line =fields.Many2one('account.analytic.account','Business Line',copy=True)
    quantity = fields.Integer('Quantities to supply',copy=True)
    product_id = fields.Many2one('product.product' ,'Product',copy=True)
    qty = fields.Integer('QTY',copy=True)

    month_plan_id = fields.Many2one('month.plan',copy=True)

    @api.depends('month_plan_id')
    @api.onchange('business_line')
    def _onchange_partner_id(self):
        #Quantity Part
        if self.business_line and self.month_plan_id.yearly_plan and self.month_plan_id.month:
            month = self.month_plan_id.month
            line =self.env['year.plan.month']
            for l in self.month_plan_id.yearly_plan.plan_line_ids:
                if l.analytic_account_id.id == self.business_line.id:
                    line = l
            if month =='jan' :
                self.quantity = line.jan
            elif month == 'feb' :
                self.quantity =line.feb
            elif month == 'mar' :
                self.quantity =line.mar
            elif month == 'apr' :
                self.quantity =line.apr
            elif month == 'may' :
                self.quantity =line.may
            elif month == 'june' :
                self.quantity =line.june
            elif month == 'july' :
                self.quantity =line.july
            elif month == 'aug' :
                self.quantity =line.aug
            elif month == 'oct' :
                self.quantity =line.oct
            elif month == 'sept' :
                self.quantity =line.sept
            elif month == 'nov' :
                self.quantity =line.nov
            elif month == 'dec' :
                self.quantity =line.dec



        # Domain Part
        domain = []
        if self.month_plan_id:
            ids=[]
            for line in self.month_plan_id.yearly_plan.plan_line_ids:
                ids.append(line.analytic_account_id.id)

            domain = [('id', 'in', ids)]
        return {'domain': {'business_line': domain}}

