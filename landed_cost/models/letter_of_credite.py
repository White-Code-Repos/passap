from odoo import fields,api,models,_
from odoo.exceptions import UserError, ValidationError

class LETTEROFCREDIT(models.Model):
    _name = 'letter.credit'
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),

        ('landed', 'Landed Cost Validation'),
        ('validated', 'Validated'),('cancel', 'Canceled')], 'State', default='draft',
        copy=False, readonly=True, track_visibility='onchange')
    name = fields.Char(
        'Name', default=lambda self: _('New'),
        copy=False, readonly=True, track_visibility='always')
    lc_number=fields.Char()
    start_date=fields.Date(default=fields.Date.context_today,readonly=True)
    end_date=fields.Date()
    payment_count = fields.Integer(compute='_get_payment_value', readonly=1)

    purchase_id=fields.Many2one('purchase.order',required=True)
    inco_term=fields.Many2one(related='purchase_id.incoterm_id',string='Inco Term')
    invoice_id=fields.Many2one('account.invoice',string="Invoice",domain="[('id', 'in',invoice_ids)]")
    total_lc_payments=fields.Float(compute='_get_payment_value',readonly=1)
    total_lc_Expense = fields.Float(compute='_get_payment_value',readonly=1)
    total_lc = fields.Float(compute='_get_payment_value',readonly=1)
    percentage = fields.Float()
    total=fields.Float(store=True)
    invoice_ids = fields.Many2many('account.invoice', compute="get_invoices")
    @api.onchange('percentage')
    def get_total_of_purchase_amount(self):
        if self.percentage:
            if self.purchase_id.amount_total:
                purchase_amount=self.purchase_id.amount_total
                self.total=self.percentage*purchase_amount

    # @api.onchange('payment_count')
    # def calculate_total_lc(self):
    #     for item in self:
    #
    #
    #         payment_id = self.env['account.payment'].search([('letter_of_credit_id', '=', self.id)])
    #         lc_expense = 0
    #         lc_payment = 0
    #         for record in payment_id:
    #             if record.payment_lc=='payment':
    #                 lc_payment+=record.amount
    #             elif record.payment_lc=='expense':
    #                 lc_expense += record.amount
    #         print(lc_expense)
    #         print(lc_payment)
    #         print(lc_payment + lc_expense)
    #         item.total_lc_payments=lc_payment
    #         item.total_lc_Expense=lc_expense
    #         item.total_lc= lc_payment + lc_expense
    #





    @api.multi
    @api.depends('payment_count')
    def _get_payment_value(self):
        for item in self:
            payment_id = self.env['account.payment'].search([('letter_of_credit_id', '=', item.id)])
            count = 0

            lc_expense = 0
            lc_payment = 0

            for record in payment_id:
                count += 1
                if record.payment_lc == 'payment':
                    if record.tax_amount1 or record.tax_amount2:
                        total_amount=record.amount+record.tax_amount1+record.tax_amount2

                        lc_payment += total_amount
                    else:
                        lc_payment += record.amount

                elif record.payment_lc == 'expense':
                    if record.tax_amount1 or record.tax_amount2:
                        total_amount = record.amount + record.tax_amount1 + record.tax_amount2

                        lc_expense += total_amount
                    else:
                        lc_expense += record.amount

            item.total_lc_payments = lc_payment
            item.total_lc_Expense = lc_expense
            item.total_lc = lc_payment + lc_expense
            item.payment_count = count



    def open_payment_view(self):
        action = self.env.ref('account.action_account_payments_payable')
        result = action.read()[0]
        result['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
        result['context'] = {'default_partner_id': self.purchase_id.partner_id.id, 'default_payment_type': 'transfer','default_payment_lc': 'payment','default_letter_of_credit_id': self.id,'default_state': 'draft','default_check_payment':True, }
        result.update({'view_type': 'form',
                       'view_mode': 'form',
                       'target': 'current',
                       })

        return result

    def open_payment_view_smart(self):
        action = self.env.ref('account.action_account_payments_payable')
        payment_id = self.env['account.payment'].search([('letter_of_credit_id', '=', self.id)])

        for item in payment_id:
            result = action.read()[0]
            result['views'] = [(self.env.ref('account.view_account_supplier_payment_tree').id, 'tree'),
                               (self.env.ref('account.view_account_payment_form').id, 'form')]
            result['domain'] = [('letter_of_credit_id', '=', self.id)]

            result.update({'view_type': 'form',
                           'view_mode': 'form' 'tree',
                           'target': 'current',
                           'res_id': item.id,

                           })


            return result




    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('letter.credit')
        return super(LETTEROFCREDIT, self).create(vals)


    @api.depends('purchase_id')
    def get_invoices(self):
        print('hello onchange')
        for item in self:

            purchase_order2 = self.env['account.invoice'].search([('origin', '=', self.purchase_id.name)])
            item.invoice_ids = purchase_order2.ids







    @api.multi
    def button_validate(self):
        for record in self:
            account_id = self.env['account.account'].search([('lc_account', '=', True)])
            payment_id = self.env['account.payment'].search([('letter_of_credit_id', '=', self.id)],limit=1)
            journal_id = self.env['account.journal'].search([('lc_account', '=', True)])

            # if self.env.user.has_group('base.group_multi_currency'):
            #     print('hello if')
            #
            #     debit_line_vals = {
            #         'name': record.name,
            #         'date': record.start_date,
            #         'payment_id': record.id,
            #         'account_id': payment_id.journal_id.default_credit_account_id.id,
            #
            #         'amount_currency': record.purchase_id.amount_total,
            #         'currency_id': payment_id.currency_id.id,
            #
            #         'debit': (record.purchase_id.amount_total / payment_id.currency_id.rate) + payment_id.currency_id.rate,
            #
            #     }
            #     credit_line_vals = {
            #
            #         'credit': (record.purchase_id.amount_total / payment_id.currency_id.rate) + payment_id.currency_id.rate,
            #         'name': record.name,
            #         'date': record.start_date,
            #         'account_id': account_id.id,
            #         'payment_id': record.id,
            #         'amount_currency': -1 * record.purchase_id.amount_total,
            #         'currency_id': payment_id.currency_id.id,
            #
            #     }
            #
            #
            #     move = record.env['account.move'].create({
            #         'state': 'draft',
            #         'journal_id': journal_id.id,
            #         'date': record.start_date,
            #         'payment_id': record.id,
            #
            #         'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
            #     })
            #
            #     payment_id.move_id = move.id
            #     record.write({'state': 'validated'})
            # else:

            debit_line_vals = {
                'name': record.name,
                'date': record.start_date,
                'payment_id': payment_id.id,
                'account_id':  account_id.id,

                'credit': record.purchase_id.amount_total,

            }
            credit_line_vals = {
                'name': record.name,
                'date': record.start_date,
                'account_id': payment_id.journal_id.default_credit_account_id.id,
                'debit': record.purchase_id.amount_total,

                'payment_id': payment_id.id,

            }
            # update ibrahim 28/2/2019
            move = record.env['account.move'].create({
                'state': 'draft',
                'journal_id': journal_id.id,
                'date': record.start_date,
                'payment_id': payment_id.id,

                'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
            })

            payment_id.move_id = move.id
            record.write({'state': 'validated'})

            action = self.env.ref('account.action_vendor_bill_template')
            invoice_id = self.env['account.invoice'].search([('id', '=', self.invoice_id.id)])
            for item in invoice_id:
                result = action.read()[0]
                result['views'] = [
                                   (self.env.ref('account.invoice_supplier_form').id, 'form')]
                result['domain'] = [('id', '=',self.invoice_id.id)]

                result.update({'view_type': 'form',
                               'view_mode': 'form' 'tree',
                               'target': 'current',
                               'res_id': item.id,

                               })

                return result


    @api.multi
    def button_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def button_draft(self):
        return self.write({'state': 'draft'})









