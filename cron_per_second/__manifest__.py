{
    'name': "Cron Per Second",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        By default Odoo cron job or schedule action cannot be used to schedule a job in seconds interval. 
        i.e You cannot schedule a cron job to run every 5 seconds.

        This module enable running cron to the lowest time fragment. It is advisable to be use for quick and fast action that 
        will take less execution time

    """,

    'author': "Babatope Ajepe",
    'website': "http://www.galago.com.ng",

    'category': 'Uncategorized',
    'version': '1.0',
    'depends': ['base'],

}
