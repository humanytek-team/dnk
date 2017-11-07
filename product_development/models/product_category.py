# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _, SUPERUSER_ID

class ProductCategory(models.Model):
    
    _inherit = "product.category"
    
    dp_form_type = fields.Selection([('flexinnova','Flexinnova'),('estatec','Estatec'),('extrupac','Extrupac')],string="DP Form To Use", required=True)