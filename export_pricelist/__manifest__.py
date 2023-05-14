{
    'name' : 'Export Customer Pricelist Odoo',
    'author': "Edge Technologies",
    'version' : '14.0.1.2',
    'live_test_url':'https://youtu.be/R7oKfmikd2Q',
    "images":["static/description/main_screenshot.png"],
    'summary' : 'Apps help customer pricelist export pricelist export sales pricelist export sale pricelist export pricelist for customer price-list export price-list export sales price-list export sale price-list export customer price list export price list for customer',
    'description' : """
        Export customer pricelist
    """,
    "license" : "OPL-1",
    'depends' : ['base','sale_management'],
    'data': [
            'security/ir.model.access.csv',
            'data/export_customer_pricelist_temp.xml',
            'wizard/export_customer_pricelist.xml',
            'report/customer_pricelist_report.xml',
            'report/customer_report_template.xml',
            ],
    'qweb' : [],
    'demo' : [],
    'installable' : True,
    'auto_install' : False,
    'price': 22,
    'currency': "EUR",
    'category' : 'Sales',
}
