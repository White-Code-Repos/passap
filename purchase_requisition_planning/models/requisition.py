from odoo import models, fields, api

class purchase_requestion(models.Model):
    _inherit = 'material.purchase.requisition'

    type = fields.Char('Requisition Type')

    month_plan = fields.Many2one('month.plan','Monthly Plan')
    business_line = fields.Many2one('account.analytic.account','Business Line')

    @api.onchange('month_plan')
    def _onchange_month_plan(self):

        # Domain Part
        domain = []
        if self.month_plan:
            ids = []
            for line in self.month_plan.plan_m_line_ids:
                ids.append(line.business_line.id)

            domain = [('id', 'in', ids)]
        return {'domain': {'business_line': domain}}

    @api.onchange('business_line')
    def _onchange_business_line(self):
        # Add Product Lines

        if self.business_line and self.month_plan:
            list=[]
            for line in self.month_plan.plan_m_line_ids:
                if line.business_line.id == self.business_line.id:
                    request_line = self.env["material.purchase.requisition.line"].create(
                        {
                            'product_id':line.product_id.id,
                            'description':line.product_id.name,
                            'qty':line.qty,
                            'uom':line.product_id.uom_id.id,
                            'requisition_type':'purchase',
                            'requisition_id':self.id,
                        })
                    list.append(request_line.id)
            self.requisition_line_ids = [(6,0,list)]

