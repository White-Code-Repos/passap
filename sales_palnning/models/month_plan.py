from odoo import models, fields, api
from datetime import datetime

class MonthPlane(models.Model):
    _name = 'month.plan'

    yearly_plan = fields.Many2one('year.plan','Yearly Plan' ,required=True)
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
                              ('dec','Dec')] ,'Month',required=True)
    source = fields.Many2one('month.plan','Version Of',readonly=True)
    plan_m_line_ids = fields.One2many('month.plan.line', 'month_plan_id')

class MonthPlaneLine(models.Model):
    _name = 'month.plan.line'

    business_line =fields.Many2one('account.analytic.account','Business Line')
    quantity = fields.Integer('Quantities to supply')
    product_id = fields.Many2one('product.product' ,'Product')
    qty = fields.Integer('QTY')

    month_plan_id = fields.Many2one('month.plan')

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

