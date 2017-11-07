# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class CRMLead(models.Model):
    _inherit = "crm.lead"
    
    dp_number = fields.Integer(compute='_compute_dp', string="Number of DPs")
    dp_ids = fields.One2many('product.development', 'opp_id', string='Orders')
    piezas_por_producto = fields.Integer("Piezas por Producto")
    precio_por_pieza = fields.Float("Precio por Pieza")

    @api.depends('dp_ids')
    def _compute_dp(self):
        for lead in self:
            lead.dp_number = len(lead.dp_ids)
    
    
    
    
