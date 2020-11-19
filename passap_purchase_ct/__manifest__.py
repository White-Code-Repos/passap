# -*- coding: utf-8 -*-
{
    'name': "Passap Purchase ct",

    'summary': """
        Passap Purchase Customisation""",

    'description': """
        Passap Purchase Customisation
    """,

    'author': "CodeTrade India Pvt. Ltd.",
    'website': "http://www.codetrade.io",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['purchase'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/res_partner_inherit.xml',
    ],
}