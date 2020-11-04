# -*- coding: utf-8 -*-
{
    'name': "Vendor Evaluation",
    'summary': """
    Vendor Evaluation""",
    'description': """
        Vendor Evaluation
    """,
    'author': "CodeTrade India Pvt. Ltd.",
    'website': "http://www.codetrade.io",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['purchase', 'stock'],
    'data': [
        'data/vendor_evaluation_data.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/purchase_order_view_ct.xml',
        'views/stock_picking_view_ct.xml',
    ],
}
