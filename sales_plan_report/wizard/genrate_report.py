from odoo import api, fields, models
from datetime import datetime


class genrate_report(models.TransientModel):
    _name = 'generate.report'

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
    month_2 = fields.Selection([('jan','Jan'),
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
                              ('dec','Dec')] ,'TO Month',required=True ,track_visibility="onchange",copy=True)
    year = fields.Selection([(num, str(num)) for num in range(1900, (datetime.now().year)+1 )], 'Year',track_visibility="onchange")
    to_date = fields.Datetime('حتي تاريخ')
    @api.multi
    def compute_actual_qty_sales(self):
        yearplan = self.env['year.plan.month'].search([])

        for year in yearplan:
            jan_qty = 0.0
            feb_qty = 0.0
            mars_qty = 0.0
            apr_qty = 0.0
            may_qty = 0.0
            jun_qty = 0.0
            jul_qty = 0.0
            aug_qty = 0.0
            oct_qty = 0.0
            sep_qty = 0.0
            nov_qty = 0.0
            dec_qty = 0.0
            sales_order = self.env['sale.order'].search([('company_id2', '=', year.company_id2.id)])

            if year.type == 'actual':
                for sale in sales_order:
                    if year.company_id2.id == sale.company_id2.id:
                        if year.year==sale.year:

                            for line in sale.order_line:

                                if sale.month == 'jan':
                                    jan_qty = jan_qty + line.product_uom_qty
                                    year.jan = jan_qty
                                elif sale.month == 'feb':
                                    feb_qty = feb_qty + line.product_uom_qty
                                    year.feb = feb_qty
                                elif sale.month == 'mar':
                                    mars_qty = mars_qty + line.product_uom_qty
                                    year.mar = mars_qty
                                elif sale.month == 'apr':
                                    apr_qty = apr_qty + line.product_uom_qty
                                    year.apr = apr_qty
                                elif sale.month == 'may':
                                    may_qty = may_qty + line.product_uom_qty
                                    year.may = may_qty
                                elif sale.month == 'june':
                                    jun_qty = jun_qty + line.product_uom_qty
                                    year.june = jun_qty
                                elif sale.month == 'july':
                                    jul_qty = jul_qty + line.product_uom_qty
                                    year.july = jul_qty
                                elif sale.month == 'aug':
                                    aug_qty = aug_qty + line.product_uom_qty
                                    year.aug = aug_qty
                                elif sale.month == 'oct':
                                    oct_qty = oct_qty + line.product_uom_qty
                                    year.oct = oct_qty
                                elif sale.month == 'sept':
                                    sep_qty = sep_qty + line.product_uom_qty
                                    year.sept = sep_qty
                                elif sale.month == 'nov':
                                    nov_qty = nov_qty + line.product_uom_qty
                                    year.nov = nov_qty
                                elif sale.month == 'dec':
                                    dec_qty = dec_qty + line.product_uom_qty
                                    year.dec = dec_qty

            elif year.type == 'diff':
                year.jan = year.jan_diff
                year.feb=year.feb_diff
                year.mar=year.mar_diff
                year.apr=year.apr_diff
                year.may=year.may_diff
                year.june=year.june_diff
                year.july=year.july_diff
                year.aug=year.aug_diff
                year.sept=year.sep_diff
                year.oct=year.oc_diff
                year.nov=year.nov_diff
                year.dec=year.dec_diff
                for sale in sales_order:
                    if year.company_id2.id == sale.company_id2.id:
                        if year.year==sale.year:

                            for line in sale.order_line:
                                if sale.month == 'jan':
                                    year.jan = year.jan - line.product_uom_qty
                                elif sale.month == 'feb':
                                    year.feb = year.feb - line.product_uom_qty
                                elif sale.month == 'mar':
                                    year.mar = year.mar - line.product_uom_qty
                                elif sale.month == 'apr':
                                    year.apr = year.apr - line.product_uom_qty
                                elif sale.month == 'may':
                                    year.may = year.may - line.product_uom_qty
                                elif sale.month == 'june':
                                    year.june = year.june - line.product_uom_qty
                                elif sale.month == 'july':
                                    year.july = year.july - line.product_uom_qty
                                elif sale.month == 'aug':
                                    year.aug = year.aug - line.product_uom_qty
                                elif sale.month == 'oct':
                                    year.oct = year.oct - line.product_uom_qty
                                elif sale.month == 'sept':
                                    year.sept = year.sept - line.product_uom_qty
                                elif sale.month == 'nov':
                                    year.nov = year.nov - line.product_uom_qty
                                elif sale.month == 'dec':
                                    year.dec = year.dec - line.product_uom_qty
            elif year.type == 'percent':

                for sale in sales_order:
                    if year.company_id2.id == sale.company_id2.id:
                        if year.year == sale.year:

                            for line in sale.order_line:
                                if sale.month == 'jan':
                                    jan_qty = jan_qty + line.product_uom_qty
                                    year.jan = (jan_qty/year.jan_percent)*100
                                elif sale.month == 'feb':
                                    feb_qty = feb_qty + line.product_uom_qty
                                    year.feb =  (feb_qty/year.feb_percent)*100
                                elif sale.month == 'mar':
                                    mars_qty = mars_qty + line.product_uom_qty
                                    year.mar = (mars_qty/year.mar_percent)*100
                                elif sale.month == 'apr':

                                    apr_qty = apr_qty + line.product_uom_qty
                                    year.apr = (apr_qty/year.apr_percent)*100
                                elif sale.month == 'may':
                                    may_qty = may_qty + line.product_uom_qty
                                    year.may =  (may_qty/year.may_percent)*100
                                elif sale.month == 'june':
                                    jun_qty = jun_qty + line.product_uom_qty
                                    year.june =(jun_qty/year.june_percent)*100
                                elif sale.month == 'july':
                                    jul_qty = jul_qty + line.product_uom_qty
                                    year.july = (jul_qty/year.july_percent)*100
                                elif sale.month == 'aug':
                                    aug_qty = aug_qty + line.product_uom_qty
                                    year.aug = (aug_qty/year.aug_percent)*100
                                elif sale.month == 'oct':
                                    oct_qty = oct_qty + line.product_uom_qty
                                    year.oct = (oct_qty/year.oc_percent)*100

                                elif sale.month == 'sept':
                                    sep_qty = sep_qty + line.product_uom_qty
                                    year.sept =  (sep_qty/year.sep_percent)*100
                                elif sale.month == 'nov':
                                    nov_qty = nov_qty + line.product_uom_qty
                                    year.nov =  (nov_qty/year.nov_percent)*100
                                elif sale.month == 'dec':
                                    dec_qty = dec_qty + line.product_uom_qty
                                    year.dec =  (dec_qty/year.dec_percent)*100

        return {
            'name': ('Planning Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'year.plan.month',
            'view_mode': 'tree',
            # 'view_type': 'tree',
            'context': {
                'group_by':['year', 'company_id2'] ,

            },
        }

    def do_report(self):
        self.ensure_one()
        data ={}
        data['form'] = self.read(['month','year'])
        year_plan = self.env['year.plan'].search([('year','=',self.year)],limit=1)

        lines = []
        for line in year_plan.plan_line_ids:
            qty = 0
            if self.month=='jan':
                qty = line.jan
            elif self.month=='feb':
                qty = line.feb
            elif self.month=='feb':
                qty = line.feb
            elif self.month=='mar':
                qty = line.mar
            elif self.month=='apr':
                qty = line.apr
            elif self.month=='may':
                qty = line.may
            elif self.month=='june':
                qty = line.june
            elif self.month=='july':
                qty = line.july
            elif self.month=='aug':
                qty = line.aug
            elif self.month=='sept':
                qty = line.sept
            elif self.month=='oct':
                qty = line.oct
            elif self.month=='nov':
                qty = line.nov
            elif self.month=='dec':
                qty = line.dec
            row={
            'brand': line.company_id2.name,
            'planed_qty': qty
            }
            lines.append(row)

        sale_orders = self.env['sale.order'].search([('year','=',self.year),('month','=',self.month)])
        for line in lines:
            saled_qty = 0
            for order in sale_orders:
                for order_line in order.order_line :
                    if line['brand'] == order_line.company_id2.name:
                        saled_qty += order_line.product_uom_qty
            line['saled_qty'] = saled_qty
            line['diff'] = line['planed_qty']-line['saled_qty']
            line['ratio'] = (line['saled_qty'] /line['planed_qty']) *100

        month2_lines=[]
        for line in year_plan.plan_line_ids:
            qty = 0
            if self.month_2 == 'jan':
                qty = line.jan
            elif self.month_2 == 'feb':
                qty = line.feb
            elif self.month_2 == 'feb':
                qty = line.feb
            elif self.month_2 == 'mar':
                qty = line.mar
            elif self.month_2 == 'apr':
                qty = line.apr
            elif self.month_2 == 'may':
                qty = line.may
            elif self.month_2 == 'june':
                qty = line.june
            elif self.month_2 == 'july':
                qty = line.july
            elif self.month_2 == 'aug':
                qty = line.aug
            elif self.month_2 == 'sept':
                qty = line.sept
            elif self.month_2 == 'oct':
                qty = line.oct
            elif self.month_2 == 'nov':
                qty = line.nov
            elif self.month_2 == 'dec':
                qty = line.dec
            row = {
                'brand': line.company_id2.name,
                'planed_qty': qty
            }
            month2_lines.append(row)
        month2_sale_orders = self.env['sale.order'].search([('year', '=', self.year), ('month', '=', self.month_2),('validity_date','<=',self.to_date)])
        for line in month2_lines:
            saled_qty = 0
            for order in month2_sale_orders:
                for order_line in order.order_line:
                    if line['brand'] == order_line.company_id2.name:
                        saled_qty += order_line.product_uom_qty
            line['saled_qty'] = saled_qty
            line['diff'] = line['planed_qty'] - line['saled_qty']
            line['ratio'] = ((line['saled_qty'] / line['planed_qty']) * 100) if line['planed_qty'] >0 else 0

        for line in lines:
            for month2_line in month2_lines:
                if line['brand'] == month2_line['brand']:
                    line['planed_qty_2'] = month2_line['planed_qty']
                    line['saled_qty_2'] = month2_line['saled_qty']
                    line['diff_2'] = month2_line['diff']
                    line['ratio_2'] = month2_line['ratio']

                    line['total_planed'] = line['planed_qty']+line['planed_qty_2']
                    line['total_saled'] = line['saled_qty']+line['saled_qty_2']
                    line['total_diff'] = line['total_planed']-line['total_saled']

                    line['final_ratio']=((line['total_saled'] / line['total_planed']) * 100) if line['total_planed']>0 else 0
        docargs = {
            'data':data['form'],
            'month1_lines': lines,
            'month2_lines': month2_lines,
            'date_year':self.year,
            'date_month':self.month,
        }

        return self.env.ref('sales_plan_report.follow_up_sales_report').report_action(self,data=docargs)