# -*- coding: utf-8 -*-
{
    'name': "Multiple Modules Uninstalled",

    'summary': """This module enable you to select and un-install multiple modules modules at a go.""",

    'description': """
        This module enable you to select and un-install multiple modules modules at a go.

        Select the modules to un-installed from the tree view and click on the action un-installed boom!!!
    """,

    'author': "Babatope Ajepe",
    'website': "http://ajepe.github.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'base',
    'version': '0.1',
    'license': 'LGPL-3',
    'images': ['static/description/main_screenshot.png'],

    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],

    # always loaded
    'data': [
        'views/module_multiple_uninstall.xml',
    ],
}
