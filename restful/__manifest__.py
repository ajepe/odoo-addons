{
    'name': 'RESTFUL API For Odoo',
    'version': '0.1.0',
    'category': 'API',
    'author': 'The InnerCircle',
    'website': 'https://ajepe.github.io/restful-api-for-odoo',
    'summary': 'RESTFUL API For Odoo',
    'support': 'galagoapps@gmail.com',
    'description': """
RESTFUL API For Odoo
====================
With use of this module user can enable REST API in any Odoo applications/modules

For detailed example of REST API refer https://ajepe.github.io/restful-api-for-odoo
""",
    'depends': [
        'web',
    ],
    'data': [
        'data/ir_config_param.xml',
        'views/ir_model.xml',
        'views/res_users.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/main_screenshot.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
