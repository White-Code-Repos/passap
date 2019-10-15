# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    vendor_evaluation_count = fields.Integer(string='Vendor Evaluations', compute='_compute_vendor_evaluation')

    def action_view_vendor_evaluation_picking(self):
        return {
            'name': _('Vendor Evaluation'),
            'view_mode': 'tree,form',
            'res_model': 'vendor.evaluation',
            'type': 'ir.actions.act_window',
            'domain': [('vendor_id', '=', self.partner_id.id)], 
        }

    def _compute_vendor_evaluation(self):
        evaluations = self.env['vendor.evaluation'].search([('vendor_id', '=', self.partner_id.id)])
        self.vendor_evaluation_count = len(evaluations)