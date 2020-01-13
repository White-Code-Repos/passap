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
    def button_validate(self):
        if any(cost.state != 'progress' for cost in self):
            raise UserError(_('Only draft landed costs can be validated'))
        if any(not cost.valuation_adjustment_lines for cost in self):
            raise UserError(_('No valuation adjustments lines. You should maybe recompute the landed costs.'))
        if not self._check_sum():
            raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))

        for cost in self:
            move = self.env['account.move']
            move_vals = {
                'journal_id': cost.account_journal_id.id,
                'date': cost.date,
                'ref': cost.name,
                'line_ids': [],
            }
            for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
                # Prorate the value at what's still in stock
                cost_to_add = (line.move_id.remaining_qty / line.move_id.product_qty) * line.additional_landed_cost

                new_landed_cost_value = line.move_id.landed_cost_value + line.additional_landed_cost
                line.move_id.write({
                    'landed_cost_value': new_landed_cost_value,
                    'value': line.move_id.value + line.additional_landed_cost,
                    'remaining_value': line.move_id.remaining_value + cost_to_add,
                    'price_unit': (line.move_id.value + line.additional_landed_cost) / line.move_id.product_qty,
                })
                # `remaining_qty` is negative if the move is out and delivered proudcts that were not
                # in stock.
                qty_out = 0
                if line.move_id._is_in():
                    qty_out = line.move_id.product_qty - line.move_id.remaining_qty
                elif line.move_id._is_out():
                    qty_out = line.move_id.product_qty
                move_vals['line_ids'] += line._create_accounting_entries(move, qty_out)

            move = move.create(move_vals)
            cost.write({'state': 'done', 'account_move_id': move.id})
            move.post()
        return True


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


