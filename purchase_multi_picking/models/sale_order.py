
from odoo import _, api, models,fields

from odoo.tools.float_utils import float_compare

from odoo.exceptions import UserError
import datetime



class SaleOrderLine(models.Model):


    _inherit = "sale.order.line"

    delivery_type_id=fields.Many2one('stock.picking.type','Delivery Type',default=1,required=True,domain="[('code','=','outgoing')]")
    split=fields.Boolean()



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()

        list_rec = []
        list_picking_type = []
        list_des=[]
        list_src=[]
        for order in self:

            for line3 in order.order_line:

                stock_move = self.env['stock.move'].create({
                     'name': line3.name or '',
                    'product_id': line3.product_id.id,
                    'product_uom': line3.product_uom.id,
                    'date': line3.order_id.date_order,
                    # 'date_expected': line3.date_planned,
                    'location_id': line3.delivery_type_id.default_location_src_id.id,
                    'location_dest_id': line3.delivery_type_id.default_location_dest_id.id,
                    'partner_id': line3.order_id.partner_id.id,
                    'move_dest_ids': [(4, x) for x in line3.move_ids.ids],
                    'state': 'draft',
                    'sale_line_id': line3.id,
                    'company_id': line3.order_id.company_id.id,
                    # 'price_unit': price_unit,
                    'picking_type_id': line3.delivery_type_id.id,
                    # 'group_id': line3.order_id.procurment_group_id.id,
                    'origin': line3.order_id.name,
                    'product_uom_qty': line3.product_uom_qty,
                    'route_ids': line3.delivery_type_id.warehouse_id and [
                        (6, 0, [x.id for x in line3.delivery_type_id.warehouse_id.route_ids])] or [],
                    'warehouse_id': line3.delivery_type_id.warehouse_id.id,
                })
                line3.move_ids = [(4, stock_move.id)]

            order.picking_ids.unlink()

            for line in order.order_line:

                for line2 in order.order_line:
                    if line.delivery_type_id == line2.delivery_type_id and line.split == False and line2.split == False:
                        list_rec.append(line.move_ids.id)
                        list_rec.append(line2.move_ids.id)
                        list_picking_type.append(line.delivery_type_id.id)
                        list_des.append(line.move_ids.location_dest_id.id)
                        list_src.append(line.move_ids.location_id.id)
                    if line != line2 and line.delivery_type_id == line2.delivery_type_id:
                        line2.split = True

                line.split = True

                if list_rec:

                    c = self.env['stock.picking'].create({'picking_type_id': list_picking_type[0],
                                                          'partner_id': order.partner_id.id,
                                                          'date': order.date_order,
                                                          'scheduled_date':order.date_order,
                                                          'origin': order.name,
                                                          'location_dest_id': list_des[0],
                                                          'location_id':list_src[0],
                                                          'company_id': order.company_id.id,
                                                          'move_ids_without_package': [(6, 0, list_rec)],
                                                          })
                    c.action_confirm()
                    c.action_assign()
                    order.picking_ids = [(4, c.id)]


                list_rec = []
                list_picking_type = []
                list_des = []
                list_src=[]

            for line in order.order_line:
                line.split = False

        return result



