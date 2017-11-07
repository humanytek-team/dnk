# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from lxml import etree

class CRMLead(models.Model):
    _inherit = "crm.lead"
    
    
    
    final_customer_id = fields.Many2one('res.partner','Final Customer')
    is_vendor = fields.Boolean('Is Vendor')
    family_id = fields.Many2one('product.category','Family', required=True)
    familysub_id = fields.Many2one('product.category','SubFamily')
    product_id = fields.Many2one('product.product','Product')
    
    
    def _onchange_partner_id_values(self, partner_id):
        res = super(CRMLead, self)._onchange_partner_id_values(partner_id)
        if res:
            partner = self.env['res.partner'].browse(partner_id)
            if partner and partner.property_product_pricelist :
                com_str = 'Distribuidor'.lower()
                pricelist_str = (partner.property_product_pricelist.name).lower()
                if com_str in pricelist_str:
                    res.update({'is_vendor': True,
                                'final_customer_id': False,
                                })
                else:
                    res.update({'is_vendor': False,
                                'final_customer_id': partner.id,
                                })
        return res
    
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CRMLead, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='family_id']"):
            categories = self.env['product.category'].search([])
            if categories:
                parent_categ = []
                for cat in categories:
                    if cat.parent_id:
                        parent_categ.append(cat.id)
                if parent_categ:
                    node.set('domain', "[('id', 'in', "+str(parent_categ)+")]")
        res['arch'] = etree.tostring(doc)
        return res
    
