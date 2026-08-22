from dateutil.relativedelta import relativedelta

from odoo import fields, models
from odoo.addons.base.models import ir_cron
from odoo.service import server

server.SLEEP_INTERVAL = 1
ir_cron._intervalTypes["seconds"] = lambda interval: relativedelta(seconds=interval)


class IrCron(models.Model):
    _inherit = "ir.cron"

    interval_type = fields.Selection(
        selection_add=[("seconds", "Seconds")], ondelete={"seconds": "cascade"}
    )
