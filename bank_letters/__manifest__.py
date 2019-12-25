{
    'name': 'Bank Letters of (Credit/Guarantee)',
    'version': '1.1',
    'author': 'Zienab Abd EL Nasser',
    'category': 'Account',
    'description': """
    Module Feature .
    ===============================================================================================
        # add letter of credit\n
        # add letter of Guarantee\n
    """,
    'depends': ['account','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/letter_of_credit_views.xml',
        'views/bank_letter_config.xml',
        'wizard/lg_draw_view.xml',
        'wizard/lg_renewal_view.xml',
        'wizard/lc_release_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
