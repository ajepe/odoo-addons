{
    "name": "Odoo RESTFUL API",
    "version": "18.0.1.0.0",
    "category": "API",
    "author": "Babatope Ajepe",
    "website": "https://ajepe.github.io/blog/restful-api-for-odoo",
    "summary": "Odoo RESTFUL API",
    "support": "ajepebabatope@gmail.com",
    "description": """ RESTFUL API For Odoo
====================
With use of this module user can enable REST API in any Odoo applications/modules

For detailed example of REST API refer https://ajepe.github.io/restful-api-for-odoo
""",
    "depends": ["web", "base_setup"],
    "data": ["views/res_users.xml", "security/ir.model.access.csv",],
    "images": ["static/description/main_screenshot.png"],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}
