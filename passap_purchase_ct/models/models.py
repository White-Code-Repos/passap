# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_confirm(self):
        super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.order_line:
                for line in order.order_line:
                    line.product_id.last_purchase_price = line.price_unit
        return True


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    name = fields.Char(string='Order #', store=True)
    qty_invoiced = fields.Float(string="Billed Qty", store=True)
    qty_received = fields.Float(string="Received Qty", store=True)
    product_qty = fields.Float(string='Ordered Qty', store=True)

    def _select(self):
        select_str = """
               WITH currency_rate as (%s)
                   SELECT
                       min(l.id) as id,
                       s.date_order as date_order,
                       s.name as name,
                       s.state,
                       s.date_approve,
                       s.dest_address_id,
                       s.partner_id as partner_id,
                       s.user_id as user_id,
                       s.company_id as company_id,
                       s.fiscal_position_id as fiscal_position_id,
                       l.product_id,
                       l.product_qty,
                       l.qty_received,
                       l.qty_invoiced,
                       p.product_tmpl_id,
                       t.categ_id as category_id,
                       s.currency_id,
                       t.uom_id as product_uom,
                       sum(l.product_qty/u.factor*u2.factor) as unit_quantity,
                       extract(epoch from age(s.date_approve,s.date_order))/(24*60*60)::decimal(16,2) as delay,
                       extract(epoch from age(l.date_planned,s.date_order))/(24*60*60)::decimal(16,2) as delay_pass,
                       count(*) as nbr_lines,
                       sum(l.price_unit / COALESCE(NULLIF(cr.rate, 0), 1.0) * l.product_qty)::decimal(16,2) as price_total,
                       avg(100.0 * (l.price_unit / COALESCE(NULLIF(cr.rate, 0),1.0) * l.product_qty) / NULLIF(ip.value_float*l.product_qty/u.factor*u2.factor, 0.0))::decimal(16,2) as negociation,
                       sum(ip.value_float*l.product_qty/u.factor*u2.factor)::decimal(16,2) as price_standard,
                       (sum(l.product_qty * l.price_unit / COALESCE(NULLIF(cr.rate, 0), 1.0))/NULLIF(sum(l.product_qty/u.factor*u2.factor),0.0))::decimal(16,2) as price_average,
                       partner.country_id as country_id,
                       partner.commercial_partner_id as commercial_partner_id,
                       analytic_account.id as account_analytic_id,
                       sum(p.weight * l.product_qty/u.factor*u2.factor) as weight,
                       sum(p.volume * l.product_qty/u.factor*u2.factor) as volume
           """ % self.env['res.currency']._select_companies_rates()
        return select_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
                s.company_id,
                s.user_id,
                s.name,
                s.partner_id,
                u.factor,
                s.currency_id,
                l.price_unit,
                s.date_approve,
                l.date_planned,
                l.product_uom,
                s.dest_address_id,
                s.fiscal_position_id,
                l.product_id,
                l.product_qty,
                l.qty_received,
                l.qty_invoiced,
                p.product_tmpl_id,
                t.categ_id,
                s.date_order,
                s.state,
                u.uom_type,
                u.category_id,
                t.uom_id,
                u.id,
                u2.factor,
                partner.country_id,
                partner.commercial_partner_id,
                analytic_account.id
        """
        return group_by_str
