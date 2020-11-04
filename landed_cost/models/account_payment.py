from odoo import fields,api,models,_
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _rec_name='payment_lc'
    letter_of_credit_id = fields.Many2one('letter.credit')
    sequenc_number = fields.Char(related="letter_of_credit_id.name",store=True)
    # payment_type = fields.Selection(string='Payment Type', required=True,selection=lambda item: item._onchange_check_payment())

    lc_expense_id = fields.Many2one('product.product', string="LC Expense Name",domain=[('landed_cost_ok','=',True)])
    payment_lc = fields.Selection([('expense', 'LC Expense'),('payment', 'LC payment')],required=True,default='payment')
    check_payment = fields.Boolean()
    tax_account1 = fields.Many2one('account.account' ,string="Tax Account")
    tax_account2 = fields.Many2one('account.account',string="Tax Account")
    tax_amount1 = fields.Float(string="Tax Amount")
    tax_amount2 = fields.Float(string="Tax Amount")

    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash', 'lc'))])

    # @api.model
    # def _onchange_check_payment(self):
    #     vals = []
    #     for record in self:
    #         if record.check_payment == False:
    #             vals.extend([('outbound', 'Send Money'), ('inbound', 'Receive Money'),('transfer', 'Internal Transfer')])
    #         else:
    #             vals.extend([('expense', 'LC Expense'),('payment', 'LC payment')])
    #     return vals


    def _compute_journal_domain_and_types(self):

        if self.check_payment == True:
            journal_type = ['bank', 'cash','lc']
            domain = []
            if self.currency_id.is_zero(self.amount) and hasattr(self, "has_invoices") and self.has_invoices:
                # In case of payment with 0 amount, allow to select a journal of type 'general' like
                # 'Miscellaneous Operations' and set this journal by default.
                journal_type = ['general']
                self.payment_difference_handling = 'reconcile'
            else:
                if self.payment_type == 'inbound':
                    domain.append(('at_least_one_inbound', '=', True))
                else:
                    domain.append(('at_least_one_outbound', '=', True))
            return {'domain': domain, 'journal_types': set(journal_type)}
        else:
            journal_type = ['bank', 'cash']
            domain = []
            if self.currency_id.is_zero(self.amount) and hasattr(self, "has_invoices") and self.has_invoices:
                # In case of payment with 0 amount, allow to select a journal of type 'general' like
                # 'Miscellaneous Operations' and set this journal by default.
                journal_type = ['general']
                self.payment_difference_handling = 'reconcile'
            else:
                if self.payment_type == 'inbound':
                    domain.append(('at_least_one_inbound', '=', True))
                else:
                    domain.append(('at_least_one_outbound', '=', True))
            return {'domain': domain, 'journal_types': set(journal_type)}





    @api.multi
    def post(self):

        if self.check_payment==False:
            """ Create the journal items for the payment and update the payment's state to 'posted'.
                A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
                and another in the destination reconcilable account (see _compute_destination_account_id).
                If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
                If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
            """
            for rec in self:
                print(rec.currency_id.rate)


                if rec.state != 'draft':
                    raise UserError(_("Only a draft payment can be posted."))

                if any(inv.state != 'open' for inv in rec.invoice_ids):
                    raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

                # keep the name in case of a payment reset to draft
                if not rec.name:
                    # Use the right sequence to set the name
                    if rec.payment_type == 'transfer':
                        sequence_code = 'account.payment.transfer'
                    else:
                        if rec.partner_type == 'customer':
                            if rec.payment_type == 'inbound':
                                sequence_code = 'account.payment.customer.invoice'
                            if rec.payment_type == 'outbound':
                                sequence_code = 'account.payment.customer.refund'
                        if rec.partner_type == 'supplier':
                            if rec.payment_type == 'inbound':
                                sequence_code = 'account.payment.supplier.refund'
                            if rec.payment_type == 'outbound':
                                sequence_code = 'account.payment.supplier.invoice'
                    rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
                        sequence_code)
                    if not rec.name and rec.payment_type != 'transfer':
                        raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

                # Create the journal entry
                amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
                move = rec._create_payment_entry(amount)
                persist_move_name = move.name

                # In case of a transfer, the first journal entry created debited the source liquidity account and credited
                # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
                if rec.payment_type == 'transfer':
                    transfer_credit_aml = move.line_ids.filtered(
                        lambda r: r.account_id == rec.company_id.transfer_account_id)
                    transfer_debit_aml = rec._create_transfer_entry(amount)
                    (transfer_credit_aml + transfer_debit_aml).reconcile()
                    persist_move_name += self._get_move_name_transfer_separator() + transfer_debit_aml.move_id.name

                rec.write({'state': 'posted', 'move_name': persist_move_name})
            return True
        else:
           used_currency = self.env.user.company_id.currency_id.with_context(company_id=self.env.user.company_id.id)
           print(used_currency.rate)
           # self.name = self.env['ir.sequence'].with_context(ir_sequence_date=self.payment_date).next_by_code('account.payment.transfer')
           if self.payment_lc =='expense':
                if self.tax_account1 or self.tax_account2 :
                    if self.env.user.has_group('base.group_multi_currency'):


                        for record in self:
                            if record.currency_id.rate >=1:
                                account_id = self.env['account.account'].search([('lc_account', '=', True)])

                                credite_amount_currency = (record.tax_amount2 + record.tax_amount1 + record.amount) * record.currency_id.rate

    
    
                                debit_line_vals = {
                                    'name': record.sequenc_number,
                                    'product_id':record.lc_expense_id.id,
                                    'date': record.payment_date,
                                    'payment_id': record.id,
                                    'account_id': account_id.id,
    
                                    'debit': record.amount * record.currency_id.rate,

                                    'amount_currency':record.amount,
                                    'currency_id': record.currency_id.id,

                                }
                                debit_line_vals2 = {
                                    'name': record.sequenc_number,
                                    'product_id': record.lc_expense_id.id,
                                    'date': record.payment_date,
                                    'payment_id': record.id,
                                    'account_id': record.tax_account1.id,
                                    'debit':   record.tax_amount1* record.currency_id.rate,

                                    'amount_currency': record.tax_amount1,
                                    'currency_id': record.currency_id.id,
                                }
                                debit_line_vals3 = {
                                    'name': record.sequenc_number,
                                    'product_id': record.lc_expense_id.id,
                                    'date': record.payment_date,
                                    'payment_id': record.id,
                                    'account_id': record.tax_account2.id,
                                    'debit': record.tax_amount2 * record.currency_id.rate,
                                    'amount_currency': record.tax_amount2,
                                    'currency_id': record.currency_id.id,

                                }
                                credit_line_vals = {
                                    'name': record.sequenc_number,
                                    'product_id': record.lc_expense_id.id,
                                    'account_id':record.journal_id.default_credit_account_id.id,
                                    'payment_id': record.id,
                                    'credit':credite_amount_currency ,
                                    'amount_currency': -1*(record.amount+record.tax_amount1+record.tax_amount2),
                                    'currency_id': record.currency_id.id,

                                }
                                # update ibrahim 28/2/2019
                                move = record.env['account.move'].create({
                                    'state': 'draft',
                                    'journal_id': record.journal_id.id,
                                    'product_id': record.lc_expense_id.id,

                                    'date': record.payment_date,
                                    'payment_id': record.id,
                                    'line_ids': [(0, 0, debit_line_vals),(0, 0, debit_line_vals2) ,(0, 0, debit_line_vals3),(0, 0, credit_line_vals)]
                                })

                                record.move_id = move.id
                                record.write({'state': 'posted'})
                            else:

                                    account_id = self.env['account.account'].search([('lc_account', '=', True)])

                                    credite_amount_currency = (record.tax_amount2 + record.tax_amount1 + record.amount) / record.currency_id.rate


                                    debit_line_vals = {
                                        'name': record.sequenc_number,
                                        'product_id': record.lc_expense_id.id,
                                        'date': record.payment_date,
                                        'payment_id': record.id,
                                        'account_id': account_id.id,

                                        'debit': record.amount / record.currency_id.rate,

                                        'amount_currency': record.amount,
                                        'currency_id': record.currency_id.id,

                                    }
                                    debit_line_vals2 = {
                                        'name': record.sequenc_number,
                                        'product_id': record.lc_expense_id.id,
                                        'date': record.payment_date,
                                        'payment_id': record.id,
                                        'account_id': record.tax_account1.id,
                                        'debit': record.tax_amount1 / record.currency_id.rate,

                                        'amount_currency': record.tax_amount1,
                                        'currency_id': record.currency_id.id,
                                    }
                                    debit_line_vals3 = {
                                        'name': record.sequenc_number,
                                        'product_id': record.lc_expense_id.id,
                                        'date': record.payment_date,
                                        'payment_id': record.id,
                                        'account_id': record.tax_account2.id,
                                        'debit': record.tax_amount2 / record.currency_id.rate,
                                        'amount_currency': record.tax_amount2,
                                        'currency_id': record.currency_id.id,

                                    }
                                    credit_line_vals = {
                                        'name': record.sequenc_number,
                                        'product_id': record.lc_expense_id.id,
                                        'account_id': record.journal_id.default_credit_account_id.id,
                                        'payment_id': record.id,
                                        'credit': credite_amount_currency,
                                        'amount_currency': -1 * (record.amount + record.tax_amount1 + record.tax_amount2),
                                        'currency_id': record.currency_id.id,

                                    }
                                    # update ibrahim 28/2/2019
                                    move = record.env['account.move'].create({
                                        'state': 'draft',
                                        'journal_id': record.journal_id.id,
                                        'product_id': record.lc_expense_id.id,

                                        'date': record.payment_date,
                                        'payment_id': record.id,
                                        'line_ids': [(0, 0, debit_line_vals), (0, 0, debit_line_vals2),
                                                     (0, 0, debit_line_vals3), (0, 0, credit_line_vals)]
                                    })

                                    record.move_id = move.id
                                    record.write({'state': 'posted'})


                    else:
                        for record in self:
                            account_id = self.env['account.account'].search([('lc_account', '=', True)])

                            debit_line_vals = {
                                'name': record.sequenc_number,
                                'product_id': record.lc_expense_id.id,
                                'date': record.payment_date,
                                'payment_id': record.id,
                                'account_id': account_id.id,

                                'debit': record.amount,

                            }
                            debit_line_vals2 = {
                                'name': record.sequenc_number,
                                'product_id': record.lc_expense_id.id,
                                'date': record.payment_date,
                                'payment_id': record.id,
                                'account_id': record.tax_account1.id,

                                'debit': record.tax_amount1,

                            }
                            debit_line_vals3 = {
                                'name': record.sequenc_number,
                                'product_id': record.lc_expense_id.id,
                                'date': record.payment_date,
                                'payment_id': record.id,
                                'account_id': record.tax_account1.id,

                                'debit': record.tax_amount2,

                            }
                            credit_line_vals = {
                                'name': record.sequenc_number,
                                'product_id': record.lc_expense_id.id,
                                'account_id': record.journal_id.default_credit_account_id.id,
                                'credit': record.amount + record.tax_amount1 + record.tax_amount2,
                                'payment_id': record.id,

                            }
                            # update ibrahim 28/2/2019
                            move = record.env['account.move'].create({
                                'state': 'draft',
                                'journal_id': record.journal_id.id,
                                'product_id': record.lc_expense_id.id,
                                'date': record.payment_date,
                                'payment_id': record.id,
                                'line_ids': [(0, 0, debit_line_vals), (0, 0, debit_line_vals2),
                                             (0, 0, debit_line_vals3), (0, 0, credit_line_vals)]
                            })

                            record.move_id = move.id
                            record.write({'state': 'posted'})

                else:
                    if self.env.user.has_group('base.group_multi_currency'):

                        for record in self:
                            if record.currency_id.rate >= 1:


                                account_id=self.env['account.account'].search([('lc_account','=',True)])



                                debit_line_vals = {
                                    'name': record.sequenc_number,
                                    'date': record.payment_date,
                                    'product_id': record.lc_expense_id.id,
                                    'payment_id': record.id,
                                    'account_id': account_id.id ,
                                    'debit':record.amount* record.currency_id.rate,
                                    'amount_currency':record.amount,
                                    'currency_id': record.currency_id.id,

                                }
                                credit_line_vals = {
                                    'name': record.sequenc_number,
                                    'account_id': record.journal_id.default_credit_account_id.id,
                                    'product_id': record.lc_expense_id.id,
                                    'amount_currency': -1*(record.amount),
                                    'credit': record.amount * record.currency_id.rate,
                                    'currency_id': record.currency_id.id,
                                    'payment_id': record.id,

                                }
                                # update ibrahim 28/2/2019
                                move = record.env['account.move'].create({
                                    'state': 'draft',
                                    'journal_id': record.journal_id.id,
                                    'product_id': record.lc_expense_id.id,
                                    'date': record.payment_date,
                                    'payment_id': record.id,

                                    'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
                                })

                                record.move_id = move.id
                                record.write({'state': 'posted'})
                            else:

                                    account_id = self.env['account.account'].search([('lc_account', '=', True)])

                                    debit_line_vals = {
                                        'name': record.sequenc_number,
                                        'date': record.payment_date,
                                        'payment_id': record.id,
                                        'account_id': account_id.id ,
                                        'debit': record.amount / record.currency_id.rate,
                                        'amount_currency': record.amount,
                                        'currency_id': record.currency_id.id,
                                        'product_id': record.lc_expense_id.id,

                                    }
                                    credit_line_vals = {
                                        'name': record.sequenc_number,
                                        'account_id': record.journal_id.default_credit_account_id.id,
                                        'amount_currency': -1 * (record.amount),
                                        'credit': record.amount / record.currency_id.rate,
                                        'currency_id': record.currency_id.id,
                                        'payment_id': record.id,
                                        'product_id': record.lc_expense_id.id,

                                    }
                                    # update ibrahim 28/2/2019
                                    move = record.env['account.move'].create({
                                        'state': 'draft',
                                        'journal_id': record.journal_id.id,
                                        'product_id': record.lc_expense_id.id,
                                        'date': record.payment_date,
                                        'payment_id': record.id,

                                        'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
                                    })

                                    record.move_id = move.id
                                    record.write({'state': 'posted'})
                    else:
                        for record in self:
                           account_id = self.env['account.account'].search([('lc_account', '=', True)])

                           debit_line_vals = {
                               'name': record.sequenc_number,
                               'product_id': record.lc_expense_id.id,
                               'date': record.payment_date,
                               'payment_id': record.id,
                               'account_id': account_id.id ,

                               'debit': record.amount,

                           }
                           credit_line_vals = {
                               'name': record.sequenc_number,
                               'product_id': record.lc_expense_id.id,
                               'account_id':  record.journal_id.default_credit_account_id.id,
                               'credit': record.amount,
                               'payment_id': record.id,

                           }
                           # update ibrahim 28/2/2019
                           move = record.env['account.move'].create({
                               'state': 'draft',
                               'journal_id': record.journal_id.id,
                               'product_id': record.lc_expense_id.id,
                               'date': record.payment_date,

                               'payment_id': record.id,
                               'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
                           })

                           record.move_id = move.id
                           record.write({'state': 'posted'})
           else:
               if self.tax_account1 or self.tax_account2 :
                   if self.env.user.has_group('base.group_multi_currency'):
                       for record in self:
                           if record.currency_id.rate >= 1:
                               account_id = self.env['account.account'].search([('lc_account', '=', True)])
                               credite_amount_currency = (record.tax_amount2 + record.tax_amount1 + record.amount) * record.currency_id.rate

                               debit_line_vals = {
                                   'name': record.sequenc_number,
                                   'date': record.payment_date,
                                   'payment_id': record.id,
                                   'account_id': account_id.id,
                                   'debit': record.amount * record.currency_id.rate,
                                   'amount_currency': record.amount,
                                   'currency_id': record.currency_id.id,
                               }
                               debit_line_vals2 = {
                                   'name':record.sequenc_number,
                                   'date': record.payment_date,
                                   'payment_id': record.id,
                                   'account_id': record.tax_account1.id,
                                   'debit': record.tax_amount1 * record.currency_id.rate,
                                   'amount_currency': record.tax_amount1,
                                   'currency_id': record.currency_id.id,

                               }
                               debit_line_vals3 = {
                                   'name': record.sequenc_number,
                                   'date': record.payment_date,
                                   'payment_id': record.id,
                                   'account_id': record.tax_account2.id,
                                   'debit': record.tax_amount2 * record.currency_id.rate,
                                   'amount_currency': record.tax_amount2,
                                   'currency_id': record.currency_id.id,


                               }
                               credit_line_vals = {
                                   'name': record.sequenc_number,
                                   'account_id': record.journal_id.default_credit_account_id.id,
                                   'payment_id': record.id,
                                   'credit': credite_amount_currency,

                                   'amount_currency':-1*(record.amount + record.tax_amount1 + record.tax_amount2),
                                   'currency_id': record.currency_id.id,


                               }
                               # update ibrahim 28/2/2019
                               move = record.env['account.move'].create({
                                   'state': 'draft',
                                   'journal_id': record.journal_id.id,
                                   'date': record.payment_date,
                                   'payment_id': record.id,
                                   'line_ids': [(0, 0, debit_line_vals), (0, 0, debit_line_vals2), (0, 0, debit_line_vals3),
                                                (0, 0, credit_line_vals)]
                               })

                               record.move_id = move.id
                               record.write({'state': 'posted'})
                           else:
                               account_id = self.env['account.account'].search([('lc_account', '=', True)])
                               credite_amount_currency = (record.tax_amount2 + record.tax_amount1 + record.amount) / record.currency_id.rate

                               debit_line_vals = {
                                   'name': record.sequenc_number,
                                   'date': record.payment_date,
                                   'payment_id': record.id,
                                   'account_id': account_id.id,
                                   'debit': record.amount / record.currency_id.rate,
                                   'amount_currency': record.amount,
                                   'currency_id': record.currency_id.id,
                               }
                               debit_line_vals2 = {
                                   'name': record.sequenc_number,
                                   'date': record.payment_date,
                                   'payment_id': record.id,
                                   'account_id': record.tax_account1.id,
                                   'debit': record.tax_amount1 /record.currency_id.rate,
                                   'amount_currency': record.tax_amount1,
                                   'currency_id': record.currency_id.id,

                               }
                               debit_line_vals3 = {
                                   'name': record.sequenc_number,
                                   'date': record.payment_date,
                                   'payment_id': record.id,
                                   'account_id': record.tax_account2.id,
                                   'debit': record.tax_amount2 / record.currency_id.rate,
                                   'amount_currency': record.tax_amount2,
                                   'currency_id': record.currency_id.id,

                               }
                               credit_line_vals = {
                                   'name': record.sequenc_number,
                                   'account_id': record.journal_id.default_credit_account_id.id,
                                   'payment_id': record.id,
                                   'credit': credite_amount_currency,

                                   'amount_currency': -1 * (record.amount + record.tax_amount1 + record.tax_amount2),
                                   'currency_id': record.currency_id.id,

                               }
                               # update ibrahim 28/2/2019
                               move = record.env['account.move'].create({
                                   'state': 'draft',
                                   'journal_id': record.journal_id.id,
                                   'date': record.payment_date,
                                   'payment_id': record.id,
                                   'line_ids': [(0, 0, debit_line_vals), (0, 0, debit_line_vals2),
                                                (0, 0, debit_line_vals3),
                                                (0, 0, credit_line_vals)]
                               })

                               record.move_id = move.id
                               record.write({'state': 'posted'})

                   else:
                           for record in self:
                               account_id = self.env['account.account'].search([('lc_account', '=', True)])

                               debit_line_vals = {
                                   'name': record.sequenc_number,
                                   'date': record.payment_date,
                                   'payment_id': record.id,
                                   'account_id': account_id.id,

                                   'debit': record.amount,

                               }
                               debit_line_vals2 = {
                                   'name': record.sequenc_number,
                                   'date': record.payment_date,
                                   'payment_id': record.id,
                                   'account_id': record.tax_account1.id,

                                   'debit': record.tax_amount1,

                               }
                               debit_line_vals3 = {
                                   'name': record.sequenc_number,
                                   'date': record.payment_date,
                                   'payment_id': record.id,
                                   'account_id': record.tax_account1.id,

                                   'debit': record.tax_amount2,

                               }
                               credit_line_vals = {
                                   'name': record.sequenc_number,
                                   'account_id': record.journal_id.default_credit_account_id.id,
                                   'credit': record.amount + record.tax_amount1 + record.tax_amount2,
                                   'payment_id': record.id,

                               }
                               # update ibrahim 28/2/2019
                               move = record.env['account.move'].create({
                                   'state': 'draft',
                                   'journal_id': record.journal_id.id,
                                   'date': record.payment_date,
                                   'payment_id': record.id,
                                   'line_ids': [(0, 0, debit_line_vals), (0, 0, debit_line_vals2),
                                                (0, 0, debit_line_vals3),
                                                (0, 0, credit_line_vals)]
                               })

                               record.move_id = move.id
                               record.write({'state': 'posted'})

               else:

                       if self.env.user.has_group('base.group_multi_currency'):
                           print('hello if')
                           for record in self:
                                if record.currency_id.rate >=1:
                                   account_id = self.env['account.account'].search([('lc_account', '=', True)])

                                   debit_line_vals = {
                                       'name': record.sequenc_number,
                                       'date': record.payment_date,
                                       'payment_id': record.id,
                                       'account_id': account_id.id ,

                                       'amount_currency': record.amount,
                                       'currency_id':record.currency_id.id,
                                       'debit': record.amount * record.currency_id.rate,



                                   }
                                   credit_line_vals = {
                                       'name': record.sequenc_number,
                                       'account_id': record.journal_id.default_credit_account_id.id,
                                        'amount_currency': -1*(record.amount),
                                       'currency_id': record.currency_id.id,
                                       'payment_id': record.id,
                                       'credit': record.amount * record.currency_id.rate,

                                   }
                                   # update ibrahim 28/2/2019
                                   move = record.env['account.move'].create({
                                       'state': 'draft',
                                       'journal_id': record.journal_id.id,
                                       'date': record.payment_date,
                                       'payment_id': record.id,

                                       'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
                                   })


                                   record.move_id = move.id
                                   record.write({'state': 'posted'})
                                else:
                                     account_id = self.env['account.account'].search([('lc_account', '=', True)])

                                     debit_line_vals = {
                                         'name': record.sequenc_number,
                                         'date': record.payment_date,
                                         'payment_id': record.id,
                                         'account_id': account_id.id,

                                         'amount_currency': record.amount,
                                         'currency_id': record.currency_id.id,
                                         'debit': record.amount / record.currency_id.rate,

                                     }
                                     credit_line_vals = {
                                         'name': record.sequenc_number,
                                         'account_id':  record.journal_id.default_credit_account_id.id,
                                         'amount_currency': -1 * (record.amount),
                                         'currency_id': record.currency_id.id,
                                         'payment_id': record.id,
                                         'credit': record.amount / record.currency_id.rate,

                                     }
                                     # update ibrahim 28/2/2019
                                     move = record.env['account.move'].create({
                                         'state': 'draft',
                                         'journal_id': record.journal_id.id,
                                         'date': record.payment_date,
                                         'payment_id': record.id,

                                         'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
                                     })

                                     record.move_id = move.id
                                     record.write({'state': 'posted'})

                       else:
                           for record in self:
                               account_id = self.env['account.account'].search([('lc_account', '=', True)])
                               print('hello else')
                               debit_line_vals = {
                                   'name': record.sequenc_number,
                                   'date': record.payment_date,
                                   'payment_id': record.id,
                                   'account_id':  account_id.id,

                                   'debit': record.amount,


                               }
                               credit_line_vals = {
                                   'name': record.sequenc_number,
                                   'account_id': record.journal_id.default_credit_account_id.id,
                                   'credit': record.amount,

                                   'payment_id': record.id,

                               }
                               # update ibrahim 28/2/2019
                               move = record.env['account.move'].create({
                                   'state': 'draft',
                                   'journal_id': record.journal_id.id,
                                   'date': record.payment_date,
                                   'payment_id': record.id,

                                   'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
                               })

                               record.move_id = move.id
                               record.write({'state': 'posted'})

    @api.model
    def create(self, vals):
        res = super(AccountPayment, self).create(vals)
        res.letter_of_credit_id.write({'state': 'progress'})
        return res


class accountLnadedPayment(models.Model):
    _name = 'account.landed.payment'
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    name = fields.Char(readonly=True, copy=False)  # The name is attributed upon post()
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('sent', 'Sent'), ('reconciled', 'Reconciled'),
                              ('cancelled', 'Cancelled')], readonly=True, default='draft', copy=False, string="Status")

    payment_reference = fields.Char(copy=False, readonly=True,
                                    help="Reference of the document used to issue this payment. Eg. check number, file name, etc.")
    move_name = fields.Char(string='Journal Entry Name', readonly=True,
                            default=False, copy=False,
                            help="Technical field holding the number given to the journal entry, automatically set when the statement line is reconciled then stored to set the same number again if the line is cancelled, set to draft and re-processed again.")

    # Money flows from the journal_id's default_debit_account_id or default_credit_account_id to the destination_account_id
    destination_account_id = fields.Many2one('account.account', compute='_compute_destination_account_id',
                                             readonly=True)
    # For money transfer, money goes from journal_id to a transfer account, then from the transfer account to destination_journal_id

    invoice_ids = fields.Many2many('account.invoice', 'account_invoice_payment_rel', 'payment_id', 'invoice_id',
                                   string="Invoices", copy=False, readonly=True, help="""Technical field containing the invoices for which the payment has been generated.
                                                                                                                                                                           This does not especially correspond to the invoices reconciled with the payment,
                                                                                                                                                                           as it can have been generated first, and reconciled later""")
    reconciled_invoice_ids = fields.Many2many('account.invoice', string='Reconciled Invoices',
                                              compute='_compute_reconciled_invoice_ids',
                                              help="Invoices whose journal items have been reconciled with this payment's.")
    has_invoices = fields.Boolean(compute="_compute_reconciled_invoice_ids",
                                  help="Technical field used for usability purposes")

    # FIXME: ondelete='restrict' not working (eg. cancel a bank statement reconciliation with a payment)
    move_line_ids = fields.One2many('account.move.line', 'payment_id', readonly=True, copy=False, ondelete='restrict')
    move_reconciled = fields.Boolean(compute="_get_move_reconciled", readonly=True)
    letter_of_credit_id = fields.Many2one('letter.credit')
    sequenc_number = fields.Char(related="letter_of_credit_id.name", store=True)
    # payment_type = fields.Selection(string='Payment Type', required=True,selection=lambda item: item._onchange_check_payment())

    lc_expense_id = fields.Many2one('product.product', string="LC Expense Name", domain=[('landed_cost_ok', '=', True)])
    payment_lc = fields.Selection([('expense', 'LC Expense'), ('payment', 'LC payment')], required=True,
                                  default='payment')
    check_payment = fields.Boolean()
    tax_account1 = fields.Many2one('account.account', string="Tax Account")
    tax_account2 = fields.Many2one('account.account', string="Tax Account")
    tax_amount1 = fields.Float(string="Tax Amount")
    tax_amount2 = fields.Float(string="Tax Amount")

    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash', 'lc'))])






