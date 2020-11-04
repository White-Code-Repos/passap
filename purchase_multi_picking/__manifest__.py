{
    'name': 'Purchase picking Type Per Line',
    'summary': 'Purchase picking Type Per Line',
    'version': '12.0.1.0.0',
    'category': 'Stock',
    'author': "ibrahim mohamed",
    'license': 'AGPL-3',
    'website':'',
    'depends': [
        'stock','sale','purchase'
    ],
    'data': [

        'data/purchase_order_data.xml',
        'views/purchase_order.xml',

        'report/purchase_order_report_template.xml',

    ],
}
