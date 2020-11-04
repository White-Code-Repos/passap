# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api




class passap_company(models.Model):
    _name = 'passap.company'
    _rec_name = 'name'

    name = fields.Char(string='Company Name')


###############################################################################

class YearPlane(models.Model):
    _inherit = 'year.plan'

    company_id2 = fields.Many2one(comodel_name="passap.company", string="Brand", required=False, )
    is_lines = fields.Boolean(string="",  )

    @api.multi
    def create_acu_diff(self):

        month_line = self.env['year.plan.month']
        for ln in self.plan_line_ids:
            month_line.write({
                'name': 'Plan'
            })
            month_line.create({
                'name': 'Actual',
                'company_id2': ln.company_id2.id,
                'year': self.year,
                'type': 'actual',


            })
            month_line.create({
                'name': 'Diff',
                'company_id2': ln.company_id2.id,
                'year': self.year,
                'type': 'diff',
                'jan': ln.jan,
                'feb': ln.feb,
                'mar': ln.mar,
                'apr': ln.apr,
                'may': ln.may,
                'june': ln.june,
                'july': ln.july,
                'aug': ln.aug,
                'sept': ln.sept,
                'oct': ln.oct,
                'nov': ln.nov,
                'dec': ln.dec,
                'jan_diff': ln.jan,
                'feb_diff': ln.feb,
                'mar_diff': ln.mar,
                'apr_diff': ln.apr,
                'may_diff': ln.may,
                'june_diff': ln.june,
                'july_diff': ln.july,
                'aug_diff': ln.aug,
                'sep_diff': ln.sept,
                'oc_diff': ln.oct,
                'nov_diff': ln.nov,
                'dec_diff': ln.dec,

            })

            month_line.create({
                'name': 'Percentage',
                'company_id2': ln.company_id2.id,
                'year': self.year,
                'type': 'percent',
                'jan': 0 ,
                'feb': 0,
                'mar': 0,
                'apr': 0,
                'may': 0,
                'june': 0,
                'july': 0,
                'aug': 0,
                'sept': 0,
                'oct': 0,
                'nov':0,
                'dec': 0,

                'jan_percent': ln.jan,
                'feb_percent': ln.feb,
                'mar_percent': ln.mar,
                'apr_percent': ln.apr,
                'may_percent': ln.may,
                'june_percent': ln.june,
                'july_percent': ln.july,
                'aug_percent': ln.aug,
                'sep_percent': ln.sept,
                'oc_percent': ln.oct,
                'nov_percent': ln.nov,
                'dec_percent': ln.dec,


            })
        self.is_lines = True

    @api.onchange('plan_line_ids')
    def get_year_plan(self):

        for line in self.plan_line_ids:
            line.year = self.year


###############################################################################

class YearPlaneMonth(models.Model):
    _inherit = 'year.plan.month'

    name = fields.Char(string="Name", required=False, )
    company_id2 = fields.Many2one(comodel_name="passap.company", string="Company", required=False, )
    year = fields.Selection([(num, str(num)) for num in range(1900, (datetime.now().year) + 1)], 'Year',
                            track_visibility="onchange",)
    type = fields.Selection(string="", selection=[('plan', 'Plan'), ('actual', 'Actual'), ('diff', 'Difference'),('percent', 'percentage') ],
                            required=False, )

    jan_diff = fields.Integer(string="", required=False, )
    feb_diff = fields.Integer(string="", required=False, )
    mar_diff = fields.Integer(string="", required=False, )
    apr_diff = fields.Integer(string="", required=False, )
    may_diff = fields.Integer(string="", required=False, )
    june_diff = fields.Integer(string="", required=False, )
    july_diff = fields.Integer(string="", required=False, )
    aug_diff = fields.Integer(string="", required=False, )
    sep_diff = fields.Integer(string="", required=False, )
    oc_diff = fields.Integer(string="", required=False, )
    nov_diff = fields.Integer(string="", required=False, )
    dec_diff = fields.Integer(string="", required=False, )

    jan_percent = fields.Float(string="", required=False, )
    feb_percent = fields.Float(string="", required=False, )
    mar_percent= fields.Float(string="", required=False, )
    apr_percent = fields.Float(string="", required=False, )
    may_percent = fields.Float(string="", required=False, )
    june_percent = fields.Float(string="", required=False, )
    july_percent = fields.Float(string="", required=False, )
    aug_percent = fields.Float(string="", required=False, )
    sep_percent = fields.Float(string="", required=False, )
    oc_percent = fields.Float(string="", required=False, )
    nov_percent = fields.Float(string="", required=False, )
    dec_percent= fields.Float(string="", required=False, )


###############################################################################

class sale_order(models.Model):
    _inherit = 'sale.order'

    company_id2 = fields.Many2one(comodel_name="passap.company", string="Brand", required=False, )
    year = fields.Char(compute="get_year_month")
    month = fields.Char(compute="get_year_month")

    @api.depends('validity_date')
    def get_year_month(self):
        if self.validity_date:
            self.year =self.validity_date.year
            month=''
            # raise Warning(type(self.confirmation_date.month))
            if self.validity_date.month==1:
                month = 'jan'
            elif self.validity_date.month==2:
                month = 'feb'
            elif self.validity_date.month==3:
                month = 'mar'
            elif self.validity_date.month==4:
                month = 'apr'
            elif self.validity_date.month==5:
                month = 'may'
            elif self.validity_date.month==6:
                month = 'june'
            elif self.validity_date.month==7:
                month = 'july'
            elif self.validity_date.month==8:
                month = 'aug'
            elif self.validity_date.month==9:
                month = 'sept'
            elif self.validity_date.month==10:
                month = 'oct'
            elif self.validity_date.month==11:
                month = 'nov'
            elif self.validity_date.month==12:
                month = 'dec'
            self.month = month


        else:
            self.year = None
            self.month = None

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    company_id2 = fields.Many2one(comodel_name="passap.company",related='order_id.company_id2', string="Brand", required=False, )



###############################################################################