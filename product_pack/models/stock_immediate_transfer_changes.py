# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import Warning, ValidationError


class StockImmediateTransferInherit(models.TransientModel):
    _inherit = 'stock.immediate.transfer'


    @api.multi
    def process(self):
        self.ensure_one()
        for pick_id in self.pick_ids:
            pick_products_move_ids = pick_id.move_lines
            if pick_products_move_ids and pick_id.picking_type_id.code == 'outgoing':
                validated = []
                for move in pick_products_move_ids:
                    if move.id in validated:
                        continue
                    if move.from_pack:
                        pack_products_moves = pick_products_move_ids.filtered(lambda l: l.parent_pack == move.parent_pack)
                        for prod_move in pack_products_moves:
                            validated.append(prod_move.id)
                            sum_quants = sum(quant.qty for quant in self.env['stock.quant'].search(
                                [('location_id', '=', prod_move.location_id.id),
                                 ('product_id', '=', prod_move.product_id.id)]))
                            print("sum_quants2", sum_quants)
                            qty_available = sum_quants
                            if qty_available < prod_move.product_uom_qty:
                                raise ValidationError(
                                    '%s available quantity is less than (%s) ' % (
                                        prod_move.product_id.name, prod_move.product_uom_qty))
        return super(StockImmediateTransferInherit, self).process()

