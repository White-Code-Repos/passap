# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):
        """
        on create picking from sale order : check if product is pack and add his pack lines insted of it
        :param vals:
        :return:
        """
        res = super(StockPickingInherit, self).create(vals)
        stock_move_obj = self.env['stock.move']
        picking_type = self.env['stock.picking.type'].browse(vals['picking_type_id'])
        if res.move_ids_without_package:
            ids = []
            for line in res.move_ids_without_package:
                ## if this product is pack product remove it and add all products on it
                if line.product_id.pack:
                    if line.open_pack:
                        for prod in line.product_id.pack_line_ids:
                            # raise Warning(line)
                            move = stock_move_obj.create({
                                'product_id': prod.product_id.id,
                                'picking_id': res.id,
                                'name': prod.product_id.name,
                                'product_uom_qty': line.product_uom_qty * prod.quantity,
                                'quantity_done': line.quantity_done,
                                'product_uom_id': line.product_uom.id,
                                'product_uom': prod.product_id.uom_id.id,
                                'state': line.state,
                                'location_id': line.location_id.id,
                                'location_dest_id': line.location_dest_id.id,
                                'date_expected': line.date_expected,
                                'move_dest_ids': [
                                    (6, 0, [x.id for x in line.move_dest_ids])] if line.move_dest_ids else False,
                                'string_availability_info': line.string_availability_info,
                                'from_pack': True,
                                'parent_pack': line.product_id.id,
                                'pack_qty': line.product_uom_qty,
                                'company_id': line.company_id.id,

                            })
                            ids.append(move.id)
                        line.write({'state': 'draft'})
                        line.unlink()
            # res.write({'move_line_ids': [(6, 0,line.ids)]})
        return res

    @api.multi
    def write(self, vals):

        res = super(StockPickingInherit, self).write(vals)
        stock_move_obj = self.env['stock.move']
        if vals.get('move_ids_without_package'):
            ids = []
            for line in self.move_ids_without_package:
                ## if this product is pack product remove it and add all products on it
                if line.product_id.pack:
                    if line.open_pack:
                        for prod in line.product_id.pack_line_ids:
                            move = stock_move_obj.create({
                                'product_id': prod.product_id.id,
                                'picking_id': self.id,
                                'name': prod.product_id.name,
                                'product_uom_qty': line.product_uom_qty * prod.quantity,
                                'quantity_done': line.quantity_done,
                                'product_uom_id': line.product_uom.id,
                                'product_uom': prod.product_id.uom_id.id,
                                'state': line.state,
                                'location_id': line.location_id.id,
                                'location_dest_id': line.location_dest_id.id,
                                'date_expected': line.date_expected,
                                'move_dest_ids': [
                                    (6, 0, [x.id for x in line.move_dest_ids])] if line.move_dest_ids else False,
                                'string_availability_info': line.string_availability_info,
                                'from_pack': True,
                                'parent_pack': line.product_id.id,
                                'pack_qty': line.product_uom_qty,
                                'company_id': line.company_id.id,

                            })
                            ids.append(move.id)
                        line.write({'state': 'draft'})
                        line.unlink()
            # res.write({'move_line_ids': [(6, 0,line.ids)]})
        return res

    @api.multi
    def button_validate(self):
        res = super(StockPickingInherit, self).button_validate()
        # pack changes
        # Zienab Abdelnasser
        self.product_pack_updates()
        return res

    @api.multi
    def product_pack_updates(self):

        for line in self.move_ids_without_package:
            # raise Warning(line.from_pack)
            if line.from_pack:
                company_user = self.env.user.company_id
                location_id = self.env['stock.location'].search([('usage', '=', 'inventory')], limit=1)
                # if location_id :
                #     # location_id = warehouse.lot_stock_id
                #     raise Warning(location_id.name)

                pack_move = self.env['stock.move'].create({
                    'state': line.state,
                    'location_id': line.location_id.id,
                    'location_dest_id': location_id.id,
                    'product_id': line.parent_pack.id,
                    'name': line.parent_pack.name,
                    'product_uom': line.product_uom.id,
                    'quantity_done': line.pack_qty,
                    'product_uom_qty': line.pack_qty,
                })

                pack_move.move_to_done()

                for product_line in line.parent_pack.pack_line_ids:
                    product_move = self.env['stock.move'].create({
                        'state': line.state,
                        'location_id': location_id.id,
                        'location_dest_id': line.location_id.id,
                        'product_id': product_line.product_id.id,
                        'name': product_line.product_id.name,
                        'product_uom': line.product_uom.id,
                        'quantity_done': line.pack_qty * product_line.quantity,
                        'product_uom_qty': line.pack_qty * product_line.quantity,
                    })
                    product_move.move_to_done()


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    @api.one
    def _process(self, cancel_backorder=False):
        self.pick_ids.product_pack_updates()
        self.pick_ids.action_done()
        if cancel_backorder:
            for pick_id in self.pick_ids:
                backorder_pick = self.env['stock.picking'].search([('backorder_id', '=', pick_id.id)])
                backorder_pick.action_cancel()
                pick_id.message_post(body=_("Back order <em>%s</em> <b>cancelled</b>.") % (backorder_pick.name))
