# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'
    
    characteristics_description = fields.Char('Characteristics Description')
    characteristics_codes = fields.Char('Characteristics Codes')

    @api.multi
    def write(self, vals):
        before_move_ids = self.move_raw_ids
        res = super(MrpProduction, self).write(vals)
        move_ids = self.move_raw_ids - before_move_ids 
        if move_ids:
            move_ids.action_confirm()
        return res
    
    
class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'
    
#     characteristics_description = fields.Char('Characteristics Description')
#     characteristics_codes = fields.Char('Characteristics Codes')
    
    
    def _prepare_mo_vals(self, bom):
        
        
        dic = {
            'origin': self.origin,
            'product_id': self.product_id.id,
            'product_qty': self.product_qty,
            'product_uom_id': self.product_uom.id,
            'location_src_id': self.rule_id.location_src_id.id or self.location_id.id,
            'location_dest_id': self.location_id.id,
            'bom_id': bom.id,
            'date_planned_start': fields.Datetime.to_string(self._get_date_planned()),
            'date_planned_finished': self.date_planned,
            'procurement_group_id': self.group_id.id,
            'propagate': self.rule_id.propagate,
            'picking_type_id': self.rule_id.picking_type_id.id or self.warehouse_id.manu_type_id.id,
            'company_id': self.company_id.id,
            'procurement_ids': [(6, 0, [self.id])],
        }
        
        
        sale_search = self.env['sale.order'].search([('name','=', str(self.group_id.name))])
        if sale_search:
            
            for order_line in sale_search.order_line:
                desc = ''
                codes = ''
                if order_line.product_id.id == self.product_id.id:
                    if order_line.characteristics:
                        for c_line in order_line.characteristics:
                            desc += str(c_line.description) + ','
                            codes += str(c_line.code) + ','
                    dic['characteristics_description'] = desc
                    dic['characteristics_codes'] = codes
        return dic
        
