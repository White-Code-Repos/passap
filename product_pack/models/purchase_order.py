from openerp import models, api ,fields


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        """
        on create picking from sale order : check if product is pack and add his pack lines insted of it
        :param vals:
        :return:
        """
        res = super(purchase_order, self).create(vals)
        purchase_order_line = self.env['purchase.order.line']
        if res.order_line:
            ids = []
            for line in res.order_line:
                ## if this product is pack product remove it and add all products on it
                if line.product_id.pack:

                        for prod in line.product_id.pack_line_ids:
                            # raise Warning(line)
                            order_line = purchase_order_line.create({
                                'product_id': prod.product_id.id,
                                'order_id': res.id,
                                'name': prod.product_id.name,
                                'product_qty': line.product_qty * prod.quantity,
                                'product_uom': prod.product_id.uom_id.id,
                                'state': line.state,
                                'price_unit':prod.product_id.lst_price,
                                'date_planned': line.date_planned,


                            })
                            ids.append(order_line.id)
                        line.write({'state': 'draft'})
                        line.write({'product_qty': 0})
        return res

    @api.multi
    def write(self, vals):

        res = super(purchase_order, self).write(vals)
        purchase_order_line = self.env['purchase.order.line']
        if vals.get('order_line'):
            ids = []
            for line in self.order_line:
                ## if this product is pack product remove it and add all products on it
                if line.product_id.pack:
                        for prod in line.product_id.pack_line_ids:
                            # raise Warning(line)
                            order_line = purchase_order_line.create({
                                'product_id': prod.product_id.id,
                                'order_id': self.id,
                                'name': prod.product_id.name,
                                'product_qty': line.product_qty * prod.quantity,
                                'product_uom': prod.product_id.uom_id.id,
                                'state': line.state,
                                'price_unit':prod.product_id.lst_price,
                                'date_planned': line.date_planned,


                            })
                            ids.append(order_line.id)
                        line.write({'state': 'draft'})
                        line.write({'product_qty': 0})

        return res


