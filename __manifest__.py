# -*- coding: utf-8 -*-
{
    'name': "tiendo_smartpurchase",

    'summary': """
        Implements the supplier selection logic for the PurchaseOrser creation method in ProcurementOrder""",

    'description': """
        As supplier allways the cheapest seller, with a valid price is selected. 
    """,

    'author': "tiendo GmbH",
    'website': "http://www.tiendo.de",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchases',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}