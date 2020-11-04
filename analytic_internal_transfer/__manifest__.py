# -*- coding: utf-8 -*-
#############################################################################

{
    'name': "Analytic Account",
    'version': "12.0.0.1",
    'summary': "Analytic account in stock move lines",
    'description': """
       This module allows you to add analytic account in stock move line and internal transfer to stock journal.
    """,
    'author': "White Code (Omnya Rashwan)",
    'website': "https://system.white-code.co.uk/web#id=1165&action=395&model=project.task&view_type=form&menu_id=263",
    'depends': ['base', 'stock', 'account'],
    'data': [
        'views/stock_move_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
