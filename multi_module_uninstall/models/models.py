# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Module(models.Model):
    _inherit = 'ir.module.module'

    @api.multi
    def module_multiple_uninstall(self):
        """ Perform the various steps required to uninstall a module completely
            including the deletion of all database structures created by the module:
            tables, columns, constraints, etc.
        """
        mods = self.browse(self.env.context.get('active_ids'))
        modules = mods.mapped('name')
        self.env['ir.model.data']._module_data_uninstall(modules)
        mods.write({'state': 'uninstalled', 'latest_version': False})
        print(modules)

    # @api.multi
    # def module_uninstall(self):

    #     modules_to_remove = self.mapped('name')
    #     
    #     self.write({'state': 'uninstalled', 'latest_version': False})
    #     return True
