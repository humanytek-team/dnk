# -*- coding: utf-8 -*-
{
    'name' : 'Custom Denker MRP',
    'version' : '1',
    'author': 'Humanytek',
    'description': """
    
    """,
    'category' : 'MRP',
    'depends' : ['mrp','sale','product','purchase'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/mrp_view.xml',
        'views/product_view.xml',
        'views/sale_view.xml',
        'views/account_invoice_view.xml',
        'views/partner_view.xml',
        'views/crm_view.xml',
        'report/crm_activity_report_views.xml',
        'views/sale_order_report_templates.xml',
        'views/report_invoice.xml',
        'views/res_config_view.xml',
    ],
    'demo': [
 
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
