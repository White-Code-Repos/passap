# -*- coding: utf-8 -*-
{
    'name' : 'landed cost Module',
    'version' : '1.0',
    'category': '',
    'description': """
   

    """,
    'depends' : ['base','stock_landed_costs','purchase','account','stock','product'],
    'data': [
        # 'security/security_groups_view.xml',
        'security/ir.model.access.csv',
        'views/stock_landed_cost.xml',
        'views/landed_cost.xml',
        'views/purchase_order.xml',
        'views/account_invoice_line.xml',
        'views/letter_of_credit.xml',
        'views/account_payment.xml',


    ],
    'installable': True,
    'application': True,
}