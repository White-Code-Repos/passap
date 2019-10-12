# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, _
# from openerp.osv import fields as old_fields
from openerp.exceptions import Warning
from odoo.exceptions import UserError
import math
import operator as py_operator

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}



class product_product(models.Model):
    _inherit = 'product.product'

    pack_line_ids = fields.One2many(
        'product.pack.line',
        'parent_product_id',
        'Pack Products',
        help='List of products that are part of this pack.'
        )
    used_pack_line_ids = fields.One2many(
        'product.pack.line',
        'product_id',
        'On Packs',
        help='List of packs where product is used.'
        )

    @api.multi
    def _product_available(
            self, field_names=None, arg=False):
        """
        For product packs we get availability in a different way
        """
        # print "IDS BEFORE: "+str(self._ids)
        pack_product_ids = self.search([
            # ('pack', '=', True),
            ('id', 'in', self._ids),
        ])
        self._ids = list(set(self._ids) - set(pack_product_ids))
        # print "IDS After: " + str(self._ids)
        res = super(product_product, self)._product_available(
            field_names, arg)
        for product in pack_product_ids:
            pack_qty_available = []
            pack_virtual_available = []
            # for subproduct in product.pack_line_ids:
            #     subproduct_stock = subproduct.product_id._product_available(field_names, arg
            #                                                )[subproduct.product_id.id]
            #     sub_qty = subproduct.quantity
            #     if sub_qty:
            #         pack_qty_available.append(math.floor(
            #             subproduct_stock['qty_available'] / sub_qty))
            #         pack_virtual_available.append(math.floor(
            #             subproduct_stock['virtual_available'] / sub_qty))
            # TODO calcular correctamente pack virtual available para negativos
            # res[product.id] = {
            #     'qty_available': (
            #         pack_qty_available and min(pack_qty_available) or False),
            #     'incoming_qty': 0,
            #     'outgoing_qty': 0,
            #     'virtual_available': (
            #         pack_virtual_available and
            #         max(min(pack_virtual_available), 0) or False),
            # }
            product.qty_available = res[product.id]['qty_available']
            product.incoming_qty = res[product.id]['incoming_qty']
            product.outgoing_qty = res[product.id]['outgoing_qty']
            product.virtual_available = res[product.id]['virtual_available']
        return res

    # def _search_product_quantity(self, operator, value, field):
    #     # TDE FIXME: should probably clean the search methods
    #     # to prevent sql injections
    #     if field not in ('qty_available', 'virtual_available', 'incoming_qty', 'outgoing_qty'):
    #         raise UserError(_('Invalid domain left operand %s') % field)
    #     if operator not in ('<', '>', '=', '!=', '<=', '>='):
    #         raise UserError(_('Invalid domain operator %s') % operator)
    #     if not isinstance(value, (float, int)):
    #         raise UserError(_('Invalid domain right operand %s') % value)
    #
    #     # TODO: Still optimization possible when searching virtual quantities
    #     ids = []
    #     for product in self.with_context(prefetch_fields=False).search([]):
    #         if OPERATORS[operator](product[field], value):
    #             ids.append(product.id)
    #     return [('id', 'in', ids)]
    #

    # overwrite ot this fields so that we can modify _product_available
    # function to support packs
    # _columns = {
    #     'qty_available': old_fields.function(
    #         _product_available, multi='qty_available',
    #         fnct_search=_search_product_quantity),
    #     'virtual_available': old_fields.function(
    #         _product_available, multi='qty_available',
    #         fnct_search=_search_product_quantity),
    #     'incoming_qty': old_fields.function(
    #         _product_available, multi='qty_available',
    #         fnct_search=_search_product_quantity),
    #     'outgoing_qty': old_fields.function(
    #         _product_available, multi='qty_available',
    #         fnct_search=_search_product_quantity),
    # }
    ## A.Salama: replaced those fields with new api defination
    qty_available = fields.Float(compute=_product_available, multi='qty_available')
    virtual_available = fields.Float(compute=_product_available, multi='qty_available')
    incoming_qty = fields.Float(compute=_product_available, multi='qty_available')
    outgoing_qty = fields.Float(compute=_product_available, multi='qty_available')

    @api.one
    @api.constrains('pack_line_ids')
    def check_recursion(self):
        """
        Check recursion on packs
        """
        pack_lines = self.pack_line_ids
        while pack_lines:
            if self in pack_lines.mapped('product_id'):
                raise Warning(_(
                    'Error! You cannot create recursive packs.\n'
                    'Product id: %s') % self.id)
            pack_lines = pack_lines.mapped('product_id.pack_line_ids')


class product_template(models.Model):
    _inherit = 'product.template'

    # TODO rename a pack_type
    pack_price_type = fields.Selection([
        ('components_price', 'Detailed - Components Prices'),
        ('totalice_price', 'Detailed - Totaliced Price'),
        ('fixed_price', 'Detailed - Fixed Price'),
        ('none_detailed_assited_price', 'None Detailed - Assisted Price'),
        ('none_detailed_totaliced_price', 'None Detailed - Totaliced Price'),
    ],
        'Pack Type',
        help="* Detailed - Components Prices: Detail lines with prices on "
        "sales order.\n"
        "* Detailed - Totaliced Price: Detail lines on sales order totalicing "
        "lines prices on pack (don't show component prices).\n"
        "* Detailed - Fixed Price: Detail lines on sales order and use product"
        " pack price (ignore line prices).\n"
        "* None Detailed - Assisted Price: Do not detail lines on sales "
        "order. Assist to get pack price using pack lines."
        )
    pack = fields.Boolean(
        'Pack?',
        help='Is a Product Pack?',
        )
    pack_line_ids = fields.One2many(
        related='product_variant_ids.pack_line_ids'
        )
    used_pack_line_ids = fields.One2many(
        related='product_variant_ids.used_pack_line_ids'
        )

    @api.constrains(
        'product_variant_ids', 'pack_price_type')
    def check_relations(self):
        """
        Check assited packs dont have packs a childs
        """
        # check assited price has no packs child of them
        if self.pack_price_type == 'none_detailed_assited_price':
            child_packs = self.mapped(
                'pack_line_ids.product_id').filtered('pack')
            if child_packs:
                raise Warning(_(
                    'A "None Detailed - Assisted Price Pack" can not have a '
                    'pack as a child!'))

        # TODO we also should check this
        # check if we are configuring a pack for a product that is partof a
        # assited pack
        # if self.pack:
        #     for product in self.product_variant_ids
        #     parent_assited_packs = self.env['product.pack.line'].search([
        #         ('product_id', '=', self.id),
        #         ('parent_product_id.pack_price_type', '=',
        #             'none_detailed_assited_price'),
        #         ])
        #     print 'parent_assited_packs', parent_assited_packs
        #     if parent_assited_packs:
        #         raise Warning(_(
        #             'You can not set this product as pack because it is part'
        #             ' of a "None Detailed - Assisted Price Pack"'))

    @api.one
    @api.constrains('company_id', 'product_variant_ids', 'used_pack_line_ids')
    def check_pack_line_company(self):
        """
        Check packs are related to packs of same company
        """
        for line in self.pack_line_ids:
            if line.product_id.company_id != self.company_id:
                raise Warning(_(
                    'Pack lines products company must be the same as the\
                    parent product company'))
        for line in self.used_pack_line_ids:
            if line.parent_product_id.company_id != self.company_id:
                raise Warning(_(
                    'Pack lines products company must be the same as the\
                    parent product company'))

    @api.multi
    def write(self, vals):
        """
        We remove from prod.prod to avoid error
        """
        if vals.get('pack_line_ids', False):
            self.product_variant_ids.write(
                {'pack_line_ids': vals.pop('pack_line_ids')})
        return super(product_template, self).write(vals)

    # @api.multi
    # def create(self,vals):
    #
    #     res = super(product_template, self).create(vals)
    #     res.product_variant_ids.write(
    #         {'pack_line_ids': vals.pop('pack_line_ids')})
    #     return res
    #

    @api.model
    def _price_get(self, products, ptype='list_price'):
        res = super(product_template, self)._price_get(
            products, ptype=ptype)
        for product in products:
            if (product.pack and product.pack_price_type in ['totalice_price',
                                                             'none_detailed_assited_price',
                                                             'none_detailed_totaliced_price']):
                pack_price = 0.0
                for pack_line in product.pack_line_ids:
                    product_line_price = pack_line.product_id.price_get()[pack_line.product_id.id] * (1 - (pack_line.discount or 0.0) / 100.0)
                    pack_price += (product_line_price * pack_line.quantity)
                res[product.id] = pack_price
        return res