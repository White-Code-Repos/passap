from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError


class AccountStatement(models.Model):
    _inherit = 'account.bank.statement'

    type_of_entry = fields.Selection(
        selection=[
            ('in', 'In'),
            ('out', 'Out')], string='Type of entry')

    serial_number = fields.Char()

    @api.model
    def create(self, vals):
        if vals['type_of_entry'] == 'in':
            vals['serial_number'] = self.env['ir.sequence'].next_by_code(
                'account.statement.in.seq')
        else:
            vals['serial_number'] = self.env['ir.sequence'].next_by_code(
                'account.statement.out.seq')
        vals['name'] = vals['serial_number']
        return super(AccountStatement, self).create(vals)


class Stock(models.Model):
    _inherit = 'stock.picking'

    def print_vendor_invoice(self):
        stock = self.env['stock.picking'].search([('id', 'in', self.env.context.get('active_ids', []))])
        partner, account, payment_terms, invoice_type, account_id, price_unit = '', '', '', '', '', 0
        products, origin = [], []
        partner_list = []

        for sto in stock:
            if sto.picking_type_id.name == 'Delivery Orders':
                invoice_type = 'out_invoice'
                view_id = self.env.ref('account.invoice_form').id
                account = sto.partner_id.property_account_receivable_id.id
            else:
                invoice_type = 'in_invoice'
                view_id = self.env.ref('account.invoice_supplier_form').id
                account = sto.partner_id.property_account_payable_id.id
            partner = sto.partner_id.id
            payment_terms = sto.partner_id.property_supplier_payment_term_id.id
            origin.append(sto.origin)

            if not partner_list:
                partner_list.append(partner)
            elif partner not in partner_list:
                raise ValidationError(_('You cannot create same bill for different partners'))

        purchase_orders = self.env['purchase.order'].search([('name', 'in', origin)])
        sale_orders = self.env['sale.order'].search([('name', 'in', origin)])

        invoice = self.env['account.invoice'].create({
            'partner_id': partner,
            'account_id': account,
            'date_invoice': datetime.now().date(),
            'type': invoice_type,
            'payment_term_id': payment_terms,
            'state': 'draft'
        })

        for sto in stock:
            for line in sto.move_ids_without_package:
                if purchase_orders:
                    journal = self.env['account.journal'].search([('type', '=', 'purchase')])
                    for pur in purchase_orders:
                        pur.update({'invoice_status': 'invoiced'})
                        for i in pur.order_line:
                            if line.product_id == i.product_id:
                                price_unit = i.price_unit
                                account_id = journal.default_debit_account_id.id
                if sale_orders:
                    journal = self.env['account.journal'].search([('type', '=', 'sale')])
                    for sal in sale_orders:
                        sal.update({'invoice_status': 'invoiced'})
                        for n in sal.order_line:
                            if line.product_id == n.product_id:
                                price_unit = n.price_unit
                                account_id = journal.default_credit_account_id.id

                product = line.product_id
                quantity = line.product_uom_qty
                invoice_lines = self.env['account.invoice.line'].create({
                    'product_id': product.id,
                    'quantity': quantity,
                    'price_unit': price_unit,
                    'invoice_id': invoice.id,
                    'name': product.name,
                    'account_id': account_id,
                })
                products.append(line.product_id.id)

        context = {'id': invoice.id,
                   'move_ids_without_package': invoice_lines}
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'context': context,
            'view_id': view_id,
            'res_id': invoice.id,
            'type': 'ir.actions.act_window',
            'target': 'self',
        }
