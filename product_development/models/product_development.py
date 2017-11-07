# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.osv import expression
from odoo.exceptions import UserError, AccessError
import re

class PDStage(models.Model):
    _name = "pd.stage"
    _description = "Stage of DP"
    _rec_name = 'name'
    _order = "sequence, name, id"


    name = fields.Char('Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    fold = fields.Boolean('Folded in Pipeline',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')


class DPFormEstilo(models.Model):
    _name = 'dp.form.estilo'
    
    name = fields.Char('Name', required=True)
    

class DPFormAditamentos(models.Model):
    _name = 'dp.form.aditamentos'
    
    name = fields.Char('Name', required=True)
    
    
class Serie(models.Model):
    _name = 'serie'
    
    name = fields.Char('Name', required=True)





class ProductDevelopment(models.Model):
    _name = "product.development"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def _default_opp_id(self):
        if self._context and self._context.get('active_model', False) == 'crm.lead':
            return self._context.get('active_id', False)
        return False
    
    def _default_stage_id(self):
        pd_stage = self.env['pd.stage'].sudo().search([])
        return pd_stage and pd_stage[0].id or False

    
    
    
    def _get_attachment(self):
        for rec in self:
            attachment_search = self.env['ir.attachment'].search([('res_model','=','product.category'),('res_id','=',rec.family_id.id)])
            print "----------attachment_search--------",attachment_search
            rec.attachment_count = len(attachment_search)
            
            
    
    attachment_count = fields.Integer(string='# of Attachments', compute='_get_attachment', readonly=True)
    
    opp_id = fields.Many2one('crm.lead','Opp. Id', required=True, default=lambda self: self._default_opp_id(), track_visibility='onchange')
    name = fields.Char(string='Folio', index=True, readonly=True, default=lambda self: _('New'))
    family_id = fields.Many2one('product.category',string='Family', related='opp_id.family_id', store=True, track_visibility='onchange')
    familysub_id = fields.Many2one('product.category',string='SubFamily', related='opp_id.familysub_id', store=True, track_visibility='onchange')
    dp_form_type = fields.Selection(related="family_id.dp_form_type",string="DP Form To Use", required=True)
    familysub_id = fields.Many2one('product.category',string='SubFamily', related='opp_id.familysub_id', store=True, track_visibility='onchange')
    final_customer_id = fields.Many2one('res.partner',string='Final Customer', related='opp_id.final_customer_id', store=True, track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Customer', related='opp_id.partner_id', store=True, track_visibility='onchange')
    contact_name = fields.Char(string='Contact Name', related='opp_id.contact_name', store=True, track_visibility='onchange')
    planned_revenue = fields.Float(string='Expected Revenue', related='opp_id.planned_revenue', store=True, track_visibility='onchange')
    stage_id = fields.Many2one('pd.stage', string='Stage', index=True, group_expand='_read_group_stage_ids', default=lambda self: self._default_stage_id(), track_visibility='onchange')
    user_id = fields.Many2one('res.users',string='User', default=lambda self: self.env.user, track_visibility='onchange')
    team_id = fields.Many2one('crm.team', string='Sales Team', related="opp_id.team_id")
    color = fields.Integer('Color Index', default=0)
    active = fields.Boolean('Active', default=True)
    
    date = fields.Datetime('Date', default=lambda self: fields.Datetime.now(), readonly=True)
    date_deadline = fields.Date('Expected Closing')
#     request = fields.Selection([('dibuio','Dibuio'),('costeo','Costeo'),('mus_fisica','Muestra Fisica')],'SE SOLICITA')
    request_dib = fields.Boolean('Dibujo')
    request_cost = fields.Boolean('Costeo')
    request_mus = fields.Boolean('Muestra Fisica')
    
    
#     is_provide = fields.Selection([('muestra_pro','Muestra Producto'),('muestra_comp','Muestra Componente'),('dibujo','DIBUJO')],'SE PROPORCIONA')
    pro_muestra = fields.Boolean('Muestra Producto')
    pro_muestra_com = fields.Boolean('Muestra Componente')
    pro_dibujo = fields.Boolean('Dibujo')
    
    piezas_opp = fields.Char('PIEZAS POR OPORTUNIDAD')
    select_1 = fields.Selection([('unico','UNICO'),('mensual','MENSUAL'),('anual','ANUAL')], 'Tiempo De Consumo')
    target_price = fields.Float('PRECIO OBJETIVO')
    
    peso = fields.Float('PESO')
#     cuidados_pieza = fields.Selection([('cosmetico','COSMETICO'),('antiestatico','ANTIESTATICO'),('abrasividad','ABRASIVIDAD'),('disipativo','DISIPATIVO')],'CUIDADOS DE LA PIEZA')
    cuidados_cos = fields.Boolean('COSMETICO')
    cuidados_antiestatico = fields.Boolean('ANTIESTATICO')
    cuidados_abrasividad = fields.Boolean('ABRASIVIDAD')
    cuidados_disipativo = fields.Boolean('DISIPATIVO')
    largo = fields.Char('LARGO')
    ancho = fields.Char('ANCHO')
    alto = fields.Char('ALTO')
    measure_unit = fields.Selection([('mm','mm'),('cm','cm'),('in','in')],'UNIDADES')
    func_de_com = fields.Char('FUNCION DEL COMPONENTE')
    
    
    tiempo_esti = fields.Selection([('0-6','0-6'),('6-12','6-12'),('12-24','12-24'),('+24','+24')],'TIEMPO DE VIDA ETIMADO (MESES)')
    largo_1 = fields.Char('LARGO')
    ancho_1 = fields.Char('ANCHO')
    alto_1 = fields.Char('ALTO')
    largo_2 = fields.Char('LARGO')
    ancho_2 = fields.Char('ANCHO')
    profundo = fields.Char('PROFUNDO')
    measure_unit_1 = fields.Selection([('mm','mm'),('cm','cm'),('in','in')],'UNIDADES')
    number_cavidades = fields.Char('Number OF Cavidades')
    contain_ref = fields.Char('CONTENEDOR REFERENCIA')
    req_pue = fields.Selection([('no','No'),('unica','Unica'),('traslapada','Traslapada')],string='REQUIERE PUERTA')
    tipo = fields.Selection([('unique','UNIQUE'),('overlap','OVERLAP')],string="TIPO")
    estibable = fields.Boolean(string='ESTIBABLE')
    maxima_estiba = fields.Char('MAXIMA ESTIBA')
    req_her = fields.Boolean('REQUIERE HERRAMENTAL')
    curf = fields.Boolean('CURF')
    eti_fle = fields.Boolean('ETIQUETA FLEXINNOVA')
    req_inst = fields.Boolean(string='REQUIERE INSTALACION')
    se_inst_con = fields.Selection([
                                    ('ret','RETAINERS'),
                                    ('tu_car','TUBER CARRIER'),
                                    ('vel','VELCRO'),
                                    ('dip','DIPSTICK'),
                                    ('tapes','TAPES'),
                                    ('other','OTHER')
                                    ], 'SE INSTALA CON')
    pro_code = fields.Char("Código del Producto")
    lugar_enter = fields.Char("Lugar de Entrega")
    #form 2
    product_id = fields.Many2one('product.product',string='Articulo', related='opp_id.product_id', store=True, track_visibility='onchange')
#     articilo = fields.Selection([('elija','Elija una opcion')], string="Articulo", track_visibility='onchange')
    um = fields.Boolean('UM are Inches', track_visibility='onchange')
    um_measure_unit = fields.Selection([('mm','mm'),('cm','cm'),('in','in')],'Unidade De Medida', track_visibility='onchange')
    tiempo_de_consumo = fields.Selection([('monthly','Monthly'),
                                          ('semestral','Semestral'),
                                          ('annual','Annual'),
                                          ('unique','Unique'),
                                          ], string="Tiempo De Consumo", track_visibility='onchange')
    moneda = fields.Many2one('res.currency', string="Moneda", track_visibility='onchange')
    nombre = fields.Char('Nombre del Proyecto', track_visibility='onchange')
    description_2 = fields.Char('Description', track_visibility='onchange')
    piezas_por_opp = fields.Float("Piezas Por Oportunidad", track_visibility='onchange')
    precio_estimado = fields.Float('Precio Estimado', track_visibility='onchange')
    importe_oportunidad = fields.Float(string="Importe Oportunidad", compute="_get_imp_opp",track_visibility='onchange')
    piezas_por_opp1 = fields.Float("Piezas Por Oportunidad", track_visibility='onchange')
    precio_estimado1 = fields.Float('Precio Estimado', track_visibility='onchange')
    importe_oportunidad1 = fields.Float(string="Importe Oportunidad", compute="_get_imp_opp1",track_visibility='onchange')
    accesorios = fields.Text('Accesorios', track_visibility='onchange')
    observaciones = fields.Text("Observaciones", track_visibility='onchange')
    muestra = fields.Boolean('Muestra')
    costeo = fields.Boolean('Costeo')
    req_spec = fields.Boolean('Spec')
    
    
    #form 3
    serie = fields.Many2one('serie','Serie')
    albertura = fields.Char("Abertura")
    altura = fields.Char("Altura")
    fuelle = fields.Char("Fuelle")
    caliber = fields.Char("Caliber")
    estilo = fields.Many2one('dp.form.estilo', 'Estilo')
    aditamentos = fields.Many2one('dp.form.aditamentos', string="Aditamentos")
    
    final_code = fields.Char('Código Final')
    des_final_code = fields.Char('Descripción del Código Final')
    rechazado = fields.Boolean('Rechazado')
    des_rejectcode = fields.Char("Comentarios de Rechazo")
    
    
    @api.depends('piezas_por_opp','precio_estimado')
    def _get_imp_opp(self):
        for dp in self:
            dp.importe_oportunidad = dp.piezas_por_opp * dp.precio_estimado
            
    @api.depends('piezas_por_opp1','precio_estimado1')
    def _get_imp_opp1(self):
        for dp in self:
            dp.importe_oportunidad1 = dp.piezas_por_opp1 * dp.precio_estimado1
            
    
    @api.onchange('date_deadline')
    def _onchange_date_deadline(self):
        if self.date_deadline:
            if self.date_deadline <= self.date:
                raise UserError(_('Please select prior date than Date + 1.'))
    
    
    @api.multi
    def action_open_attachment(self):
        attachment_search = self.env['ir.attachment'].search([('res_model','=','product.category'),('res_id','=',self.family_id.id)])
        action = self.env.ref('product_development.action_attachment_dnk').read()[0]
        if len(attachment_search) > 1:
#             action['views'] = [(self.env.ref('base.view_attachment_tree').id, 'tree')]
            action['domain'] = [('id', 'in', attachment_search.ids)]
        elif len(attachment_search) == 1:
            action['views'] = [(self.env.ref('product_development.view_attachment_form_dnk').id, 'form')]
            action['res_id'] = attachment_search.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action 
    
    
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('product.development') or _('New')
        return super(ProductDevelopment, self).create(vals)
    
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)
    
    @api.multi
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}
    
    
