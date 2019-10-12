# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import Warning


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    from_pack = fields.Boolean(default=False, readonly=True)
    parent_pack = fields.Many2one('product.product', string="Parent Pack", default=False, readonly=True)
    pack_qty = fields.Float(readonly=True)

    is_pack = fields.Boolean(related='product_id.pack',readonly=True)
    open_pack = fields.Boolean(default=False)

    @api.multi
    def move_to_done(self):
        # raise Warning("lol")
        for move in self:
            move._action_confirm()
            move._action_assign()
            # This creates a stock.move.line record.
            # You could also do it manually using self.env['stock.move.line'].create({...})
            # raise Warning(zek)
            move.move_line_ids.write({'qty_done': move.product_uom_qty})
            move._action_done()

            return 


