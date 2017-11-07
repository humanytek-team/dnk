# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    import_export_legend = fields.Text(related="company_id.import_export_legend", string="Import & Export Legend")
