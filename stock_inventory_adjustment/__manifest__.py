# -*- coding: utf-8 -*-
{
    'name': "Stock Inventory Adjustment Enhancement",

    'summary': """
    Add new date to add inventory adjustment in old date.
""",
    'description': """
    """,
    'website': "",
    'author': "White Code - Omnya Rashwan",
    'category': 'stock',
    'version': '12.1',
    'depends': ['base', 'hr', 'stock', 'product'],
    'data': [
        'views/stock_move_line_view.xml',
        'views/stock_inventory_view.xml',
    ]
}
