from odoo import fields,api,models,_,tools
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from collections import defaultdict

class LANDEDCOST(models.Model):
    _inherit = 'stock.landed.cost'
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('done', 'Posted'),
        ('cancel', 'Cancelled')], 'State', default='draft',
        copy=False, readonly=True, track_visibility='onchange')

    purchase_id = fields.Many2one('purchase.order')
    inco_term = fields.Many2one(related='purchase_id.incoterm_id',string='Inco Term')
    invoice_id = fields.Many2one('account.invoice',string="Invoice",domain="[('id', 'in',invoice_ids)]")
    picking_ids = fields.Many2many(
        'stock.picking', string='Transfers',
        copy=False, states={'done': [('readonly', True)]},domain="[('id', 'in',picking_idss)]")
    # picking_ids_test = fields.Many2many(
    #     'stock.picking', string='Transfers',
    #     copy=False, states={'done': [('readonly', True)]}, domain="[('id', 'in',picking_idss)]")
    landed_cost_check = fields.Boolean()
    invoice_ids=fields.Many2many('account.invoice',compute="get_picking")
    picking_idss=fields.Many2many('stock.picking',compute="get_picking")

    @api.depends('purchase_id')
    def get_picking(self):
        print('hello onchange')
        for item in self:
            if item.landed_cost_check==True and item.purchase_id:
                purchase_order = self.env['stock.picking'].search([('origin', '=', self.purchase_id.name)])
                purchase_order2 = self.env['account.invoice'].search([('origin', '=', self.purchase_id.name)])
                item.invoice_ids=purchase_order2.ids
                item.picking_idss=purchase_order.ids
            else:
                purchase_order = self.env['stock.picking'].search([])
                purchase_order2 = self.env['account.invoice'].search([])
                item.invoice_ids = purchase_order2.ids
                item.picking_idss = purchase_order.ids




    @api.multi
    def button_validate(self):
        if self.landed_cost_check==True:


            if any(cost.state != 'progress' for cost in self):
                raise UserError(_('Only draft landed costs can be validated'))
            if any(not cost.valuation_adjustment_lines for cost in self):
                raise UserError(_('No valuation adjustments lines. You should maybe recompute the landed costs.'))
            if not self._check_sum():
                raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))

            for cost in self:
                print('for loop')
                letter_credit_id = self.env['letter.credit'].search([('purchase_id', '=', self.purchase_id.id)])
                letter_credit_id.write({'state': 'landed'})
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
        else:
            if any(cost.state != 'draft' for cost in self):
                raise UserError(_('Only draft landed costs can be validated'))
            if any(not cost.valuation_adjustment_lines for cost in self):
                raise UserError(_('No valuation adjustments lines. You should maybe recompute the landed costs.'))
            if not self._check_sum():
                raise UserError(
                    _('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))

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

    @api.multi
    def update_cost_line(self):

        letter_credit_id = self.env['letter.credit'].search([('purchase_id', '=', self.purchase_id.id)])

        for line in self.cost_lines:
                payment_total = 0
                payment_sum=0
                for letter in letter_credit_id:
                    payment_id = self.env['account.payment'].search(
                        [('letter_of_credit_id', '=', letter.id), ('payment_lc', '=', 'expense'),('lc_expense_id', '=', line.product_id.id)])


                    for payment in payment_id:

                            payment_total += payment.amount + payment.tax_amount1 + payment.tax_amount2



                    for rec in payment_id:
                        print(payment_total)
                        if rec.currency_id.rate >= 1:
                            payment_sum=payment_total *rec.currency_id.rate

                        else:
                                payment_sum = payment_total / rec.currency_id.rate


                line.update({'price_unit':payment_sum})






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

    @api.multi
    def compute_landed_cost(self):
        if self.landed_cost_check == False:

            AdjustementLines = self.env['stock.valuation.adjustment.lines']
            AdjustementLines.search([('cost_id', 'in', self.ids)]).unlink()

            digits = dp.get_precision('Product Price')(self._cr)
            towrite_dict = {}
            for cost in self.filtered(lambda cost: cost.picking_ids):
                total_qty = 0.0
                total_cost = 0.0
                total_weight = 0.0
                total_volume = 0.0
                total_line = 0.0
                all_val_line_values = cost.get_valuation_lines()
                for val_line_values in all_val_line_values:
                    for cost_line in cost.cost_lines:
                        val_line_values.update({'cost_id': cost.id, 'cost_line_id': cost_line.id})
                        self.env['stock.valuation.adjustment.lines'].create(val_line_values)
                    total_qty += val_line_values.get('quantity', 0.0)
                    total_weight += val_line_values.get('weight', 0.0)
                    total_volume += val_line_values.get('volume', 0.0)

                    former_cost = val_line_values.get('former_cost', 0.0)
                    # round this because former_cost on the valuation lines is also rounded
                    total_cost += tools.float_round(former_cost, precision_digits=digits[1]) if digits else former_cost

                    total_line += 1

                for line in cost.cost_lines:
                    value_split = 0.0
                    for valuation in cost.valuation_adjustment_lines:
                        value = 0.0
                        if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                            if line.split_method == 'by_quantity' and total_qty:
                                per_unit = (line.price_unit / total_qty)
                                value = valuation.quantity * per_unit
                                print(value)
                            elif line.split_method == 'by_weight' and total_weight:
                                per_unit = (line.price_unit / total_weight)
                                value = valuation.weight * per_unit
                            elif line.split_method == 'by_volume' and total_volume:
                                per_unit = (line.price_unit / total_volume)
                                value = valuation.volume * per_unit
                            elif line.split_method == 'equal':
                                value = (line.price_unit / total_line)
                                print(value)
                            elif line.split_method == 'by_current_cost_price' and total_cost:
                                per_unit = (line.price_unit / total_cost)
                                value = valuation.former_cost * per_unit
                            else:
                                value = (line.price_unit / total_line)

                            if digits:
                                value = tools.float_round(value, precision_digits=digits[1], rounding_method='UP')
                                fnc = min if line.price_unit > 0 else max
                                value = fnc(value, line.price_unit - value_split)
                                value_split += value

                            if valuation.id not in towrite_dict:
                                towrite_dict[valuation.id] = value
                            else:
                                towrite_dict[valuation.id] += value
            for key, value in towrite_dict.items():
                AdjustementLines.browse(key).write({'additional_landed_cost': value})

            return True
        else:
            print('else code')
            AdjustementLines = self.env['stock.valuation.adjustment.lines']
            AdjustementLines.search([('cost_id', 'in', self.ids)]).unlink()

            digits = dp.get_precision('Product Price')(self._cr)
            towrite_dict = {}
            for cost in self.filtered(lambda cost: cost.picking_ids):
                total_qty = 0.0
                total_cost = 0.0
                total_weight = 0.0
                total_volume = 0.0
                total_line = 0.0
                cost_custom=0.0
                cost_non_custom=0.0
                all_val_line_values = cost.get_valuation_lines()
                for val_line_values in all_val_line_values:
                    for cost_line in cost.cost_lines:
                        val_line_values.update({'cost_id': cost.id, 'cost_line_id': cost_line.id})
                        self.env['stock.valuation.adjustment.lines'].create(val_line_values)
                    total_qty += val_line_values.get('quantity', 0.0)
                    total_weight += val_line_values.get('weight', 0.0)
                    total_volume += val_line_values.get('volume', 0.0)

                    former_cost = val_line_values.get('former_cost', 0.0)
                    # round this because former_cost on the valuation lines is also rounded
                    total_cost += tools.float_round(former_cost, precision_digits=digits[1]) if digits else former_cost

                    total_line += 1

                for line in cost.cost_lines:
                    value_split = 0.0
                    for valuation in cost.valuation_adjustment_lines:
                        value = 0.0
                        if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                            if line.split_method == 'by_quantity' and total_qty:
                                per_unit = (line.price_unit / total_qty)
                                value = valuation.quantity * per_unit
                                print(value)
                            elif line.split_method == 'by_weight' and total_weight:
                                per_unit = (line.price_unit / total_weight)
                                value = valuation.weight * per_unit
                            elif line.split_method == 'by_volume' and total_volume:
                                per_unit = (line.price_unit / total_volume)
                                value = valuation.volume * per_unit
                            elif line.split_method == 'equal':
                                value = (line.price_unit / total_line)
                                print(value)
                            elif line.split_method == 'by_current_cost_price' and total_cost:
                                per_unit = (line.price_unit / total_cost)
                                value = valuation.former_cost * per_unit
                            elif line.split_method == 'custom' and total_cost:
                                for invoice in self.invoice_id:
                                    for invoice_line in self.invoice_id.invoice_line_ids:
                                        if line.product_id.custom_percentage == True:
                                            if invoice_line.product_id.id == valuation.product_id.id:

                                                cost_custom =invoice.custom_total_egp
                                                percentage_line= invoice_line.price_subtotal/invoice.amount_total
                                                print(percentage_line)


                                                per_unit = cost_custom*percentage_line

                                                value = per_unit
                                        else:
                                            if invoice_line.product_id.id == valuation.product_id.id:
                                                cost_non_custom = invoice_line.non_custom_percent

                                                per_unit = line.price_unit * cost_non_custom
                                                value = per_unit
                            else:
                                value = (line.price_unit / total_line)

                            if digits:
                                value = tools.float_round(value, precision_digits=digits[1], rounding_method='UP')
                                fnc = min if line.price_unit > 0 else max
                                value = fnc(value, line.price_unit - value_split)
                                value_split += value

                            if valuation.id not in towrite_dict:
                                towrite_dict[valuation.id] = value
                            else:
                                towrite_dict[valuation.id] += value
            for key, value in towrite_dict.items():
                AdjustementLines.browse(key).write({'additional_landed_cost': value})

            return True
    def _check_sum(self):
        """ Check if each cost line its valuation lines sum to the correct amount
        and if the overall total amount is correct also """
        prec_digits = self.env.user.company_id.currency_id.decimal_places
        for landed_cost in self:
            total_amount = sum(landed_cost.valuation_adjustment_lines.mapped('additional_landed_cost'))
            if not tools.float_is_zero(total_amount - landed_cost.amount_total, precision_digits=prec_digits):
                return False

            val_to_cost_lines = defaultdict(lambda: 0.0)
            for val_line in landed_cost.valuation_adjustment_lines:
                val_to_cost_lines[val_line.cost_line_id] += val_line.additional_landed_cost
            if any(not tools.float_is_zero(cost_line.price_unit - val_amount, precision_digits=prec_digits)
                   for cost_line, val_amount in val_to_cost_lines.items()):
                return False
        return True



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


