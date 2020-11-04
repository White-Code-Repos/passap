# -*- coding: utf-8 -*-

{
    'name': 'Custom Account Statement Module',
    'version': '12.0',
    'summary': '',
    'category': 'Accounting',
    'description': """
    Add New button on inventory to create invoice or bill for more than selected Receipt order or Delivery order
    """,
    'website': '',
    'depends': ['base', 'account', 'account_accountant','stock'],
    'data': [
        'data/account_statement_data.xml',
        'data/account_vendor_invoice_data.xml',
        'views/account_statement_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
