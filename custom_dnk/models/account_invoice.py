# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    
    
    customer_code = fields.Char('Customer Product Code')
    product_weight = fields.Float("Total Weight(Kgs)", compute="_get_product_weight", store=True)
    
    @api.multi
    @api.depends('product_id','quantity')
    def _get_product_weight(self):
        for line in self:
            if line.product_id and line.product_id.weight > 0.0 and line.quantity > 0.0:
                line.product_weight = line.product_id.weight * line.quantity
    
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        res =  super(AccountInvoiceLine, self)._onchange_product_id()
        self.customer_code = False
        if self.product_id and self.product_id.customer_ids:
            for cus_info in self.product_id.customer_ids:
                if cus_info.name.id == self.invoice_id.partner_id.id:
                    self.customer_code =  cus_info.product_code
        return res