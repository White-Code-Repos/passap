# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009  Àngel Àlvarez - NaN  (http://www.nan-tic.com)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Product Pack',
    'version': '10.0.1.3.3',
    'category': 'Product',
    'sequence': 14,
    'summary': '',
    'description': """
Product Pack
============
Withilist:
----------
* TODO correctly calculate virtual pack available for negatives.
* Check if product is pack and add its pack lines instead of it.
    """,
    'author':  'NaN·tic, ADHOC, upgrade to V10: Ahmed Salama <asalama@zadsolutions.com>, Dalia Atef <datef@zadsolutions.com> , Zienab Abd EL Nasser',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'stock','sale','sales_team','product'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pack_view.xml',
        'views/sale_view.xml',
        'views/product_view_changes.xml',
        'views/stock_picking_changes.xml',
    ],
    'demo': [
        # 'demo/demo_data.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
