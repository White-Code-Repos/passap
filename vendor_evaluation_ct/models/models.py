# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VendorEvaluationCT(models.Model):
    _name = 'vendor.evaluation'
    _rec_name = 'number_evaluation'

    number_evaluation = fields.Char(string='Number')
    vendor_id = fields.Many2one('res.partner', 'Vendor', domain=[('supplier', '=', True)])
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    responsible = fields.Many2one(comodel_name='res.partner')
    evaluation_ids = fields.One2many(comodel_name='evaluation.info', inverse_name='eval_id', string='Evaluation')
    notes = fields.Text(string='Terms and conditions')
    purchase_ids = fields.Many2many('purchase.order', compute="get_purchase_orders")

    @api.model
    def create(self, vals):
        vals['number_evaluation'] = self.env['ir.sequence'].next_by_code('vendor.evaluation')
        res = super(VendorEvaluationCT, self).create(vals)
        return res

    # @api.depends('vendor_id')
    # def get_purchase_orders(self):
    #     print('hello onchange')
    #     list=[]
    #     for item in self:
    #         for rec in item.evaluation_ids:
    #             rec.write({'partner_id':item.vendor_id.id})
    #             # purchase_order2 = self.env['purchase.order'].search([('partner_id', '=', self.vendor_id.id)])
    #             # item.purchase_ids = purchase_order2.ids
    #             # for rec in purchase_order2:
                #     list.append(rec.id)
                #     print(rec.id)
                #     # item.evaluation_ids.purchase_number=rec.id

                # return {'domain': {'evaluation_ids.purchase_number': [('id', 'in',purchase_order2.ids)]}
                #
                #         }


class Evaluation(models.Model):
    _name = 'evaluation.info'

    purchase_number = fields.Many2one(comodel_name='purchase.order',domain="[('partner_id', '=',partner_id)]")
    quality_delivery = fields.Integer(string='Quality Delivery')
    delivery_date = fields.Date(string='Delivery Date')
    quantity = fields.Integer(string='Quantity')
    price = fields.Float(string='Price')
    partner_id = fields.Many2one(related="eval_id.vendor_id",store=True)

    # Relational field
    eval_id = fields.Many2one(comodel_name='vendor.evaluation')

    @api.onchange('purchase_number')
    def get_purchase_orders(self):
        quantity=0
        for item in self:

                for line in item.purchase_number.order_line:
                    quantity +=line.product_qty
                item.quantity=quantity
                item.price=item.purchase_number.amount_total



