# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.osv import expression
import re

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    characteristics_ok = fields.Boolean('Characteristics OK')
    customer_ids = fields.One2many('product.customerinfo', 'product_tmpl_id', 'Customers')


class ProductProduct(models.Model):
    _inherit = "product.product"
    
    customer_code = fields.Char('Internal Reference', compute='_compute_customer_product_code')
    customer_ref = fields.Char('Customer Ref', compute='_compute_customer_ref')
    
    @api.one
    def _compute_customer_product_code(self):
        for cus_info in self.customer_ids:
            if cus_info.name.id == self._context.get('partner_id'):
                self.customer_code = cus_info.product_code or self.default_code
        else:
            self.customer_code = self.default_code

    @api.one
    def _compute_customer_ref(self):
        for cus_info in self.customer_ids:
            if cus_info.name.id == self._context.get('partner_id'):
                product_name = cus_info.product_name or self.default_code
        else:
            product_name = self.name
        self.customer_ref = '%s%s' % (self.customer_code and '[%s] ' % self.customer_code or '', product_name)
        
    
    @api.multi
    def name_get(self):
        # TDE: this could be cleaned a bit I think

        def _name_get(d):
            name = d.get('name', '')
            code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            if code:
                name = '[%s] %s' % (code,name)
            return (d['id'], name)

        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        result = []
        for product in self.sudo():
            # display only the attributes with multiple possible values on the template
            variable_attributes = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id')
            variant = product.attribute_value_ids._variant_name(variable_attributes)

            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            customers = []
            if partner_ids:
                sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and (x.product_id == product)]
                if not sellers:
                    sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and not x.product_id]
                customers = [x for x in product.customer_ids if (x.name.id in partner_ids) and (x.product_id == product)]
                if not customers:
                    customers = [x for x in product.customer_ids if (x.name.id in partner_ids) and not x.product_id]
            if customers:
                for c in customers:
                    seller_variant = c.product_name and (
                        variant and "%s (%s)" % (c.product_name, variant) or c.product_name
                        ) or False
                    mydict = {
                              'id': product.id,
                              'name': seller_variant or name,
                              'default_code': c.product_code or product.default_code,
                              }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
            
            elif sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                        variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                        ) or False
                    mydict = {
                              'id': product.id,
                              'name': seller_variant or name,
                              'default_code': s.product_code or product.default_code,
                              }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
            
            else:
                mydict = {
                          'id': product.id,
                          'name': name,
                          'default_code': product.default_code,
                          }
                result.append(_name_get(mydict))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            products = self.env['product.product']
            if operator in positive_operators:
                products = self.search([('default_code', '=', name)] + args, limit=limit)
                if not products:
                    products = self.search([('barcode', '=', name)] + args, limit=limit)
            if not products and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                products = self.search(args + [('default_code', operator, name)], limit=limit)
                if not limit or len(products) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(products)) if limit else False
                    products += self.search(args + [('name', operator, name), ('id', 'not in', products.ids)], limit=limit2)
            elif not products and operator in expression.NEGATIVE_TERM_OPERATORS:
                products = self.search(args + ['&', ('default_code', operator, name), ('name', operator, name)], limit=limit)
            if not products and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    products = self.search([('default_code', '=', res.group(2))] + args, limit=limit)
            # still no results, partner in context: search on supplier info as last hope to find something
            if not products and self._context.get('partner_id'):
                customers = self.env['product.customerinfo'].search([
                    ('name', '=', self._context.get('partner_id')),
                    '|',
                    ('product_code', operator, name),
                    ('product_name', operator, name)])
                if customers:
                    products = self.search([('product_tmpl_id.customer_ids', 'in', customers.ids)], limit=limit)
                
                else:
                    suppliers = self.env['product.supplierinfo'].search([
                    ('name', '=', self._context.get('partner_id')),
                    '|',
                    ('product_code', operator, name),
                    ('product_name', operator, name)])
                    if suppliers:
                        products = self.search([('product_tmpl_id.seller_ids', 'in', suppliers.ids)], limit=limit)
        else:
            products = self.search(args, limit=limit)
        return products.name_get()
    
    

class CustomerInfo(models.Model):
    _name = "product.customerinfo"
    _description = "Information about a product Customer"
    _order = 'sequence'

    name = fields.Many2one(
        'res.partner', 'Customer',
        domain=[('customer', '=', True)], ondelete='cascade', required=True,
        help="Customer of this product")
    product_name = fields.Char('Customer Product Name')
    product_code = fields.Char('Customer Product Code')
    sequence = fields.Integer('Sequence', default=1)
    product_id = fields.Many2one('product.product', 'Product Variant')   
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', index=True, ondelete='cascade')