# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from datetime import datetime, timedelta
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"
     
    state = fields.Selection(selection_add=[('expedition', 'Expedition'),
                                            ('auth_expedition','Authorized Expedition'),
                                            ('reject_expedition','Expedition Rejected')
                                            ])
    
    
    @api.multi
    def action_accept_expedition(self):
        for order in self:
            order.write({'was_sent': False,'state': 'auth_expedition'})
            
    @api.multi
    def action_reject_expedition(self):
        for order in self:
            create_date = datetime.strptime(str(order.date_order),"%Y-%m-%d %H:%M:%S")
            for line in order.order_line:
                if line.check_delivery_date:
                    product_delivery_date = timedelta(days=(line.product_id.sale_delay)) + create_date
                    line.write({'product_delivery_date' :product_delivery_date,'check_delivery_date': False})
            order.write({'was_sent': False,'state': 'reject_expedition'})
            
    @api.multi
    def action_quotation_send(self):
        res = super(SaleOrder,self).action_quotation_send()
        if self.state in ('auth_expedition','reject_expedition'):
            self.state = 'sale'
            self.was_sent = True
        return res
                    
    
    @api.multi
    def action_confirm(self):
        res = super(SaleOrder,self).action_confirm()
        for order in self:
            order._add_customer_to_product()
    
    
    @api.multi
    def _add_customer_to_product(self):
        for line in self.order_line:
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            if partner not in line.product_id.customer_ids.mapped('name'):
                currency = partner.property_purchase_currency_id or self.env.user.company_id.currency_id
                supplierinfo = {
                    'name': partner.id,
                    'sequence': max(line.product_id.customer_ids.mapped('sequence')) + 1 if line.product_id.customer_ids else 1,
                }
                vals = {
                    'customer_ids': [(0, 0, supplierinfo)],
                }
                try:
                    line.product_id.write(vals)
                except AccessError:  # no write access rights -> just ignore
                    break
                

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    
    characteristics_ok = fields.Boolean('Characteristics OK')
    characteristics = fields.One2many('sale.order.line.characteristic', 'order_line_id', 'Characteristics')
    customer_code = fields.Char('Customer Product Code')
    product_weight = fields.Float("Total Weight(Kgs)", compute="_get_product_weight", store=True)
    
    
    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        res.check_deliverydate(vals.get('product_delivery_date', False))
#         if res.check_delivery_date:
#             res.order_id.state = 'expedition'
#         elif self.order_id.state == 'expedition' and not self.check_delivery_date:
#             self.order_id.state = 'draft'
        return res
    
    @api.multi
    def write(self, vals):
        self.check_deliverydate(vals.get('product_delivery_date', False))
        res = super(SaleOrderLine, self).write(vals)
        if self.check_delivery_date and self.order_id.state == 'sale':
            self.order_id.state = 'expedition'
        elif self.order_id.state == 'expedition' and not self.check_delivery_date:
            self.order_id.state = 'sale'
        return res
    
    
    @api.multi
    def check_deliverydate(self, del_date=False):
        if del_date:
            date_order = self.convert_tz(self.order_id.date_order)
            create_date = datetime.strptime(str(date_order),"%Y-%m-%d %H:%M:%S")
            product_delivery_date = create_date
            product_delivery_date = datetime.strptime(str(product_delivery_date),"%Y-%m-%d %H:%M:%S")
#             product_delivery_date = product_delivery_date +timedelta(days=1)
            new_product_delivery_date = del_date
            new_product_delivery_date = datetime.strptime(str(new_product_delivery_date),"%Y-%m-%d")
            new_product_delivery_date = new_product_delivery_date.replace(hour=23,minute=59,second=59)
            if new_product_delivery_date <= product_delivery_date:
                raise ValidationError(_('La fecha de entrega del producto '+self.product_id.name+' no puede ser menor a '\
                    +str(product_delivery_date)+'.\nPor favor cambiela por otra.'))
            weekno = new_product_delivery_date.weekday()
            if weekno > 4:
                raise ValidationError(_('FINES DE SEMANA NO SON VALIDOS PARA ENTREGA, FAVOR DE SELECCIONAR OTRO DÍA'))
            
    
    @api.multi
    @api.depends('product_id','product_uom_qty')
    def _get_product_weight(self):
        for line in self:
            if line.product_id and line.product_id.weight > 0.0 and line.product_uom_qty > 0.0:
                line.product_weight = line.product_id.weight * line.product_uom_qty
    
    
    @api.multi
    @api.onchange('product_id','characteristics','characteristics.extra_price')
    def product_id_change(self):
        res =  super(SaleOrderLine, self).product_id_change()
        self.customer_code = False
        if self.product_id and self.product_id.customer_ids:
            for cus_info in self.product_id.customer_ids:
                if cus_info.name.id == self._context.get('partner_id'):
                    self.customer_code =  cus_info.product_code
                
        if self.product_id and self.product_id.characteristics_ok == True:
            total = 0.0
            for ch in self.characteristics:
                total += ch.extra_price
            final_total = total + self.price_unit
            self.price_unit = final_total
            self.characteristics_ok = True
        else:
            self.characteristics_ok = False
        return res
    
    
    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine,self)._prepare_invoice_line(qty)
        res.update({'customer_code': self.customer_code})
        return res
        
        
    
    
    
class SaleOrderLineCharacteristic(models.Model):
    _name = 'sale.order.line.characteristic'
    
    name = fields.Char('Name')
    code = fields.Char('Code')
    description = fields.Char('Description')
    extra_price = fields.Float('Product Price', digits=dp.get_precision('Product Price'))
    order_line_id = fields.Many2one("sale.order.line",'Sale Order Line')
#     product_id = fields.Many2one(related='order_line_id.product_id', store=True, string='Product', readonly=True)



