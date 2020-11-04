# -*- coding: utf-8 -*-

{
    'name': 'Custom Stock Valuation Module',
    'version': '12.0',
    'summary': '',
    'category': 'Stock',
    'description': """
    Add location id in inventory valuation when choose specific date
    """,
    'website': '',
    'depends': ['base', 'stock_enterprise', 'stock_account_enterprise'],
    'data': [
        'views/inventory_valuation_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
