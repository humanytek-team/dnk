# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResAgent(models.Model):
    _name = 'res.agent'
    
    name = fields.Char('Name', required=True)

class PartnerInvLeyend(models.Model):
    _name = 'partner.inv.leyend'
    
    name = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], required=True, string="Mes")
    broker_id = fields.Many2one('res.agent','Agente Aduanal')
    rfc = fields.Char('RFC')
    patent = fields.Char('Patente')
    ex_number = fields.Char('Exportación')
    im_number = fields.Char('Importación')
    partner_id = fields.Many2one('res.partner','Partner')
    


class Partner(models.Model):
    _inherit = "res.partner"
    
    
    is_final_customer = fields.Boolean('Is a Final Customer ?')
    immex = fields.Char('Immex')
    part_inv_line = fields.One2many('partner.inv.leyend','partner_id','Line')
    
    
    @api.multi
    @api.onchange('is_final_customer')
    def final_customer_change(self):
        if self.is_final_customer:
            self.write({'customer': False,'supplier': False})
            
    @api.multi
    @api.onchange('customer','supplier')
    def customer_supplier_change(self):
        if self.customer or self.supplier:
            self.is_final_customer = False