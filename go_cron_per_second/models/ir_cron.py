from dateutil.relativedelta import relativedelta

import odoo
from odoo import fields, models

odoo.service.server.SLEEP_INTERVAL = 1
odoo.addons.base.models.ir_cron._intervalTypes["seconds"] = lambda interval: relativedelta(seconds=interval)


class IRCron(models.Model):
    _inherit = "ir.cron"

    interval_type = fields.Selection(selection_add=[("seconds", "Seconds")])
