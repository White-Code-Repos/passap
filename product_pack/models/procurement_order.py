# -*- coding: utf-8 -*-
from openerp import models, fields, api,_
from openerp.exceptions import Warning


class ProcurementOrder(models.Model):
    _inherit = 'procurement.rule'

    @api.multi
    def _run_move(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        if self.action == 'move':
            if not self.location_src_id:
                self.message_post(body=_('No source location defined!'))
                return False
            # create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            group_id = False
            if self.group_propagation_option == 'propagate':
                group_id = values.get('group_id', False) and values['group_id'].id
            elif self.group_propagation_option == 'fixed':
                group_id = self.group_id.id
            move_values = self._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
            parent_move = self.env['stock.move'].sudo().create(move_values)
            if parent_move.product_id.pack and parent_move.picking_type_id.code == 'outgoing':
                for line in parent_move.product_id.pack_line_ids:
                    move_values['product_id'] = line.product_id.id
                    move_values['name'] = line.product_id.name
                    move_values['product_uom_qty'] = line.quantity * parent_move.product_uom_qty
                    move_values['from_pack'] = True
                    move_values['parent_pack'] = parent_move.product_id.id
                    self.env['stock.move'].sudo().create(move_values)
                parent_move.unlink()
            return True
        return super(ProcurementOrder, self)._run_move(product_id, product_qty, product_uom, location_id, name, origin, values)

