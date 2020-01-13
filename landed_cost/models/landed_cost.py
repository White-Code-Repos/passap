from odoo import fields,api,models,_
from odoo.exceptions import UserError, ValidationError

class LANDEDCOST(models.Model):
    _inherit = 'stock.landed.cost'
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('done', 'Posted'),
        ('cancel', 'Cancelled')], 'State', default='draft',
        copy=False, readonly=True, track_visibility='onchange')
    purchase_id=fields.Many2one('purchase.order')
    inco_term=fields.Many2one(related='purchase_id.incoterm_id',string='Inco Term')
    invoice_id=fields.Many2one('account.invoice',string="Invoice",store=True)


    @api.multi
    def button_progress(self):
        for item in self:
            purchase_order=self.env['account.invoice'].search([('origin','=',self.purchase_id.name)])
            if purchase_order:
                for rec in purchase_order:
                     item.invoice_id = rec.id

                return self.write({'state': 'progress'})
            else:
                raise UserError(_('Sorry you can not confirm landed cost before Create  invoice   for Purchase order (%s)')%(item.purchase_id.name))


    @api.model
    def create(self, vals):
        res=super(LANDEDCOST, self).create(vals)

        for item in res:
            lc_products = self.env['product.product'].search([])
            for product in lc_products:
                for inco in product.income_terms:
                    if item.inco_term == inco:
                        valss = {
                            'cost_id': item.id,
                            'product_id': product.id,
                            'name': product.name,
                            'account_id': product.property_account_expense_id.id,
                            'split_method': product.split_method,
                            'price_unit': product.standard_price,

                        }

                        res.cost_lines.create(valss)
        return  res




    # @api.depends('purchase_id')
    # def get_inco_products(self):
    #     print('hello onchange')
    #     for item in self:
    #         print(self.id)
    #         lc_products=self.env['product.product'].search([])
    #         for product in lc_products:
    #             for inco in product.income_terms:
    #                 if item.inco_term == inco:
    #                   vals={
    #                         'cost_id':30,
    #                         'product_id': product.id,
    #                         'name':product.name,
    #                         'account_id': product.property_account_expense_id.id,
    #                         'split_method': product.split_method,
    #                         'price_unit': product.standard_price,
    #
    #                     }
    #                   # item.sudo().create({'cost_lines':vals})
    #





class LANDEDCOSTLines(models.Model):
    _inherit = 'stock.landed.cost.lines'
    SPLIT_METHOD = [
        ('equal', 'Equal'),
        ('custom', 'BY Custom Percentage'),
        ('by_quantity', 'By Quantity'),
        ('by_current_cost_price', 'By Current Cost'),
        ('by_weight', 'By Weight'),
        ('by_volume', 'By Volume'),
    ]

    split_method = fields.Selection(selection=SPLIT_METHOD, string='Split Method', required=True)


