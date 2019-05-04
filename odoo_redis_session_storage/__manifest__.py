# Copyright 2019 Babatope Ajepe
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Redis Session Store",
    "version": "1.0.0",
    "depends": ["base"],
    "author": "Babatope Ajepe",
    "license": 'LGPL-3',
    "description": """Use redis server as the session storage instead
    of default Odoo filesystem implmentation, for high availaiblity
    and to boost and enhanc Odoo speed.

    """,
    "summary": """Using Redis for storing sessions is a great way to get more performance out of load balanced odoo servers.""",
    "website": "",
    "category": 'API',
    "auto_install": False,
    "installable": True,
    "application": False,
    'currency': 'EUR',
    'price': 130.00,
    'images': ['static/description/main_screenshot.jpg'],
    "external_dependencies": {
        'python': ['redis'],
    },
}
