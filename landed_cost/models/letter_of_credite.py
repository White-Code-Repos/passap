from odoo import fields,api,models,_
from odoo.exceptions import UserError, ValidationError

class LETTEROFCREDIT(models.Model):
    _name = 'letter.credit'
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('confirm', 'Confirmed'),
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




    purchase_id=fields.Many2one('purchase.order')
    inco_term=fields.Many2one(related='purchase_id.incoterm_id',string='Inco Term')
    invoice_id=fields.Many2one('account.invoice',string="Invoice",store=True)


    def _get_payment_value(self):
        payment_id = self.env['account.payment'].search([('letter_of_credit_id', '=', self.id)])
        count = 0
        for rec in payment_id:
            count += 1
        self.payment_count = count



    def open_payment_view(self):
        action = self.env.ref('account.action_account_payments_payable')
        result = action.read()[0]
        result['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
        result['context'] = {'default_partner_id': self.purchase_id.partner_id.id, 'default_payment_type': 'payment','default_letter_of_credit_id': self.id,'default_state': 'draft', }
        result.update({'view_type': 'form',
                       'view_mode': 'form',
                       'target': 'current',
                       })

        return result

    def open_payment_view_smart(self):
        action = self.env.ref('account.action_account_payments_payable')
        payment_id = self.env['account.payment'].search([])

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

    @api.multi
    def button_confirm(self):


        return self.write({'state': 'progress'})

    @api.multi
    def button_confirm_lc(self):
        return self.write({'state': 'confirm'})

    @api.multi
    def button_lc_validate(self):
        return self.write({'state': 'landed'})

    @api.multi
    def button_validate(self):
        return self.write({'state': 'validated'})

    @api.multi
    def button_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def button_draft(self):
        return self.write({'state': 'draft'})









