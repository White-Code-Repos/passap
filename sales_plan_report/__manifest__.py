# -*- coding: utf-8 -*-
{
    'name': "Sales Planning Report",

    'summary': """Can Show Plan Qty To all Company and Actual Qty Sale and Diffrence between This
        """,

    'description': """
        Can Show Plan Qty To all Company and Actual Qty Sale and Diffrence between This
    """,

    'author': "Whit Code & Elsayed IRaky",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','sales_palnning','sale','account'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/sale_order.xml',
        'views/sales_followup_report.xml',
        'wizard/genrate_report.xml',
        'views/purchase_order.xml',
        'reports/plan_reports.xml',
    ],
}