# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Opportunity, Client, Activity Date, Activity, Responsible, Activity Summary, 
# Stage, Closing Date, Conclusion

from odoo import fields, models, tools


class ActivityReportDNK(models.Model):

    _name = "crm.activity.report.dnk"
    _auto = False
    _description = "DNK CRM Activity Analysis"
    _rec_name = 'id'

    
    lead_id = fields.Many2one('crm.lead', "Opportunity", readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner/Customer', readonly=True)
    final_customer_id = fields.Many2one('res.partner','Final Customer')
    date = fields.Datetime('Activity Date', readonly=True)
    next_activity_id = fields.Many2one('crm.activity', 'Activity', readonly=True)
    user_id = fields.Many2one('res.users', 'Responsible', readonly=True)
    state = fields.Selection(
        required=True,
        selection=[
                ('new', 'New'),
                ('closed', 'Closed'),
                ('canceled', 'Canceled'),
        ],
        default='new',
    )
    date_deadline = fields.Date('Closing Date')
    title_action = fields.Char('Activity Summary')
    note = fields.Html('Note')
    lead_type = fields.Char(
        string='Type',
        selection=[('lead', 'Lead'), ('opportunity', 'Opportunity')],
        help="Type is used to separate Leads and Opportunities")
    reason_to_close = fields.Text('Reason To Cancel/Close')

    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_activity_report_dnk')
        self._cr.execute("""
            CREATE VIEW crm_activity_report_dnk AS (
                select
                    cl.id,
                    cl.create_date as date,
                    cl.next_activity_id,
                    cl.date_deadline,
                    cl.title_action,
                    l.id as lead_id,
                    cl.user_id,
                    cl.state_act as state,
                    cl.note,
                    l.partner_id,
                    l.type as lead_type,
                    cl.reason_to_close,
                    l.final_customer_id
                from
                    "crm_activity_log_persistent" cl
                    
                    join "crm_lead" l on (cl.lead_id = l.id)

            )""")
