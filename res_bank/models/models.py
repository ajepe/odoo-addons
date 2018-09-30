# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResBank(models.Model):

    _inherit = 'res.bank'

    nuban = fields.Boolean(string='NUBAN')