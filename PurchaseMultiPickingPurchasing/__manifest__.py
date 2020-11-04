# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name': "PurchaseMultiPickingPurchasing",
    'version': "11.0.0.1",
    'summary': "This module allows you to create separate shipment per Purchase order line.",
    'category': 'Purchases',
    'description': """
        This module allows you to create separate shipment per Purchase order line.
        purchase multi shipment
        purchase multi pickings
        different shipment by purchase order lines
        different shipment by purchase lines
        separate shipment by purchase order lines
        separate shipment by purchase order
        separate picking by purchase order lines
        separate picking by purchase order
    """,
    'author': "Sitaram",
    'website': " ",
    'depends': ['base','purchase','stock','purchase_stock'],
    'data': [
        'views/purchase.xml'
    ],
    'demo': [],
    "license": "AGPL-3",
    'images': ['static/description/banner.png'],
    'live_test_url': 'https://youtu.be/6pql7VwPPjo',
    'installable': True,
    'application': True,
    'auto_install': False,
}
