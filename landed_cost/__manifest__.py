# -*- coding: utf-8 -*-
{
    'name' : 'letter of credit of landed cost Module',
    'version' : '1.0',
    'category': '',
    'description': """
    letter of credit of landed cost Module help to create letter of credit for purchase order
    and landed cost 
    when letter of credit is validated the company can take action belongs to the purchase order which related to the letter of credit
   

    """,
    'depends' : ['base','stock_landed_costs','purchase','account','stock','product','purchase_stock'],
    'data': [

        'security/ir.model.access.csv',
        'views/stock_landed_cost.xml',
        'views/landed_cost.xml',
        'views/purchase_order.xml',
        'views/account_invoice_line.xml',
        'views/letter_of_credit.xml',
        'views/account_payment.xml',
        'views/account_move_line.xml',


    ],
    'installable': True,
    'application': True,
}