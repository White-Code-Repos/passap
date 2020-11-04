from odoo import fields,api,models,_
from odoo.exceptions import UserError, ValidationError

class PURCHASEORDER(models.Model):
    _inherit = 'purchase.order'
    letter_of_credit = fields.Boolean()
    lc_count = fields.Integer(compute='_get_lc_value',readonly=1)

    def _get_lc_value(self):
        lc_id = self.env['stock.landed.cost'].search([('purchase_id', '=', self.id)])
        count = 0
        for rec in lc_id:
            count += 1
        self.lc_count = count

    @api.multi
    def button_confirm(self):
        result = super(PURCHASEORDER, self).button_confirm()
        if self.letter_of_credit == True:
            print('hello if')
            account_record = self.env['account.journal'].search([('lc_account', '=', True)])

            vals = {'purchase_id': self.id,
                    'state': 'draft',
                    'landed_cost_check': True,
                    'account_journal_id': account_record.id,
                    }
            self.env['stock.landed.cost'].create(vals)
            self.env['letter.credit'].create(vals)


            return result
        else:
           return result








    def open_lc_view(self):
        action = self.env.ref('stock_landed_costs.action_stock_landed_cost')
        lc_id = self.env['stock.landed.cost'].search([])


        for item in lc_id:
                result = action.read()[0]
                result['views'] = [(self.env.ref('stock_landed_costs.view_stock_landed_cost_tree').id, 'tree'),(self.env.ref('stock_landed_costs.view_stock_landed_cost_form').id, 'form')]
                result['domain'] = [('purchase_id', '=', self.id)]

                result.update({'view_type': 'form',
                               'view_mode': 'form' 'tree',
                               'target': 'current',
                               'res_id': item.id,
                               })

                return result

    # @api.multi
    # def create_lc_record(self):
    #    # vals= {'purchase_id': self.id,
    #    #        'state': 'draft',
    #    #   }
    #    # self.env['letter.credit'].create(vals)
    #
    #    account_record=self.env['account.journal'].search([('lc_account','=',True)])
    #    print('journal',account_record)
    #    action = self.env.ref('stock_landed_costs.action_stock_landed_cost')
    #    result = action.read()[0]
    #    result['views'] = [(self.env.ref('stock_landed_costs.view_stock_landed_cost_form').id, 'form')]
    #    result['context'] = {'default_purchase_id': self.id, 'default_state': 'draft','default_account_journal_id':account_record.id, }
    #    result.update({'view_type': 'form',
    #                   'view_mode': 'form',
    #                   'target': 'current',
    #                   })
    #
    #    return result
    # @api.multi
    # def action_view_invoice(self):
    #     if self.letter_of_credit ==False:
    #
    #         '''
    #         This function returns an action that display existing vendor bills of given purchase order ids.
    #         When only one found, show the vendor bill immediately.
    #         '''
    #         action = self.env.ref('account.action_vendor_bill_template')
    #         result = action.read()[0]
    #         create_bill = self.env.context.get('create_bill', False)
    #         # override the context to get rid of the default filtering
    #         result['context'] = {
    #             'type': 'in_invoice',
    #             'default_purchase_id': self.id,
    #             'default_currency_id': self.currency_id.id,
    #             'default_company_id': self.company_id.id,
    #             'company_id': self.company_id.id
    #         }
    #         # choose the view_mode accordingly
    #         if len(self.invoice_ids) > 1 and not create_bill:
    #             result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
    #         else:
    #             res = self.env.ref('account.invoice_supplier_form', False)
    #             form_view = [(res and res.id or False, 'form')]
    #             if 'views' in result:
    #                 result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
    #             else:
    #                 result['views'] = form_view
    #             # Do not set an invoice_id if we want to create a new bill.
    #             if not create_bill:
    #                 result['res_id'] = self.invoice_ids.id or False
    #         result['context']['default_origin'] = self.name
    #         result['context']['default_reference'] = self.partner_ref
    #         return result
    #     else:
    #         '''
    #                    This function returns an action that display existing vendor bills of given purchase order ids.
    #                    When only one found, show the vendor bill immediately.
    #                    '''
    #         action = self.env.ref('account.action_vendor_bill_template')
    #         result = action.read()[0]
    #         create_bill = self.env.context.get('create_bill', False)
    #         # override the context to get rid of the default filtering
    #         result['context'] = {
    #             'type': 'in_invoice',
    #             'default_purchase_id': self.id,
    #             'default_currency_id': self.currency_id.id,
    #             'default_company_id': self.company_id.id,
    #             'company_id': self.company_id.id
    #         }
    #         # choose the view_mode accordingly
    #         if len(self.invoice_ids) > 1 and not create_bill:
    #             result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
    #         else:
    #             res = self.env.ref('account.invoice_supplier_form', False)
    #             form_view = [(res and res.id or False, 'form')]
    #             if 'views' in result:
    #                 result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
    #             else:
    #                 result['views'] = form_view
    #             # Do not set an invoice_id if we want to create a new bill.
    #             if not create_bill:
    #                 result['res_id'] = self.invoice_ids.id or False
    #         result['context']['default_origin'] = self.name
    #         result['context']['default_reference'] = self.partner_ref
    #
    #
    #         action = self.env.ref('stock_landed_costs.action_stock_landed_cost')
    #         result = action.read()[0]
    #         result['views'] = [(self.env.ref('stock_landed_costs.view_stock_landed_cost_form').id, 'form')]
    #         result['context'] = {'default_purchase_id': self.id, 'default_state':'draft', }
    #         result.update({'view_type': 'form',
    #                        'view_mode': 'form',
    #                        'target': 'current',
    #                        })
    #
    #
    #         return result


class ProductTemplateCustom(models.Model):
    _inherit = "product.template"
    SPLIT_METHOD = [
        ('equal', 'Equal'),
        ('custom','BY Custom Percentage'),
        ('by_quantity', 'By Quantity'),
        ('by_current_cost_price', 'By Current Cost'),
        ('by_weight', 'By Weight'),
        ('by_volume', 'By Volume'),
    ]

    split_method = fields.Selection(
        selection=SPLIT_METHOD, string='Split Method', default='equal',
        help="Equal : Cost will be equally divided.\n"
             "By Quantity : Cost will be divided according to product's quantity.\n"
             "By Current cost : Cost will be divided according to product's current cost.\n"
             "By Weight : Cost will be divided depending on its weight.\n"
             "By Volume : Cost will be divided depending on its volume.")