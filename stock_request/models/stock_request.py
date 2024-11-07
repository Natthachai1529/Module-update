# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions
from odoo.tools import float_compare
import time
from datetime import datetime,timedelta
from odoo.exceptions import UserError


_STATES = [
    ('draft', 'Draft'),
    ('wait_approve', 'Waiting Approve'),
    ('done', 'Done'),
    ('rejected', 'Rejected'),
    ('cancel', 'Cancelled')
]


class StockRequest(models.Model):

    _name = 'stock.request'
    _description = 'Stock Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    @api.depends('requested_by', 'state')
    def _compute_director(self):
        for order in self:
            emp = self.env['hr.employee'].search([
                ('user_id', '=', order.requested_by.id),
            ])
            if emp and emp[0].parent_director_ids:
                director = emp[0].parent_director_ids.ids
                order.director_user_ids = director

    @api.model
    def _get_default_requested_by(self):
        return self.env['res.users'].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].get('stock.request')

    @api.model
    def _get_default_warehouse(self):
        warehouse_obj = self.env['stock.warehouse']
        company_id = self.env['res.users'].browse(
            self.env.uid).company_id.id
        warehouse = warehouse_obj.search([('company_id', '=', company_id)],
                                         limit=1)
        return warehouse

    @api.depends('name', 'origin', 'date_start',
                 'requested_by', 'assigned_to', 'description', 'company_id',
                 'line_ids', 'warehouse_id')
    def _get_is_editable(self):
        if self.state in ('wait_approve', 'done', 'rejected'):
            self.is_editable = False
        else:
            self.is_editable = True

    @api.onchange('stock_type_id')
    def on_change_res_partner(self):
        if self.stock_type_id and self.stock_type_id.default_partner_id:
            self.partner_id = self.stock_type_id.default_partner_id.id
        else:
            self.partner_id = ''
        if self.stock_type_id and self.stock_type_id.stock_location_id:
            self.stock_location_id = self.stock_type_id.stock_location_id.id

    @api.model
    def _default_res_partner(self):
        return self.on_change_res_partner()

    name = fields.Char(
        'Request Reference',
        size=32,
        required=True,
        default='New',
        readonly=True
    )
    origin = fields.Char(
        'Source Document',
        size=32
    )
    date_start = fields.Date(
        'Creation date',
        help="Date when the user initiated therequest.",
        default=lambda *args:
        time.strftime('%Y-%m-%d %H:%M:%S'),
        tracking=True,
    )
    note = fields.Text(
        string='Note',
        readonly=False,
    )
    requested_by = fields.Many2one(
        'res.users',
        'Requested by',
        required=True,
        tracking=True,
        default=_get_default_requested_by
    )
    assigned_to = fields.Many2one(
        'res.users',
        'Approver',
        tracking=True,
    )
    description = fields.Text(
        'Description'
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        default=lambda self: self.env.company,
    )
    line_ids = fields.One2many(
        'stock.request.line',
        'request_id',
        'Products to Purchase',
        readonly=False,
        tracking=True,
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
       string='Warehouse',
       default=_get_default_warehouse,
       tracking=True,
    )
    state = fields.Selection(
        selection=_STATES,
        string='Status',
        tracking=True,
        required=True,
        default='draft'
    )
    schedule_date = fields.Datetime(
        'Schedule Date',
        default=lambda *args: time.strftime('%Y-%m-%d %H:%M:%S'),
        tracking=True,
    )
    delivery_note = fields.Text(
        string='Delivery Note',
        readonly=False,
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order Reference",
    )
    purchase_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Select',
        domain="[('state','=','purchase')]",
    )
    purchase_ids = fields.Many2many(
        comodel_name='purchase.order',
        string='Purchase',
        domain="[('state','=','purchase')]",
    )
    project_id = fields.Many2one(
        'project.project',
        string="Project",
    )
    is_editable = fields.Boolean(
        string="Is editable",
        compute="_get_is_editable",
        readonly=True
    )
    remine_ids = fields.One2many(
        comodel_name="stock.request.remine",
        inverse_name="request_id",
        string="Remind",
        required=False,
    )
    director_user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Director',
#         compute='_compute_director',
    )
    is_sale_more = fields.Boolean(
        string="การขายสินค้าเพิ่มเติม"
    )
    stock_type = fields.Selection(
        selection=[
#             ('asset', 'Asset'),
            ('production', 'Production'),
            ('project', 'Project'),
            ('back_office', 'Back Office'),
            ('service', 'Service'),
            ('transfer_spare', 'Shop Consignment'),
            ('sample_product', 'Sample Product'),
        ],
        string='Stock Type(old)',
        required=False,
    )
    stock_type_id = fields.Many2one(
        comodel_name='stock.request.type',
        string='Request Type',
    )
    cancel_reason = fields.Char(
        string='Cancel Reason',
        tracking=True,
    )
    reject_reason = fields.Char(
        string='Reject Reason',
        tracking=True,
    )
    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Picking',
    )
    delivered_status = fields.Char(
        string='Delivery Status',
        compute='_compute_delivered_status',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        default=_default_res_partner,
        required=True,
        check_company=True,
    )
    po_customer = fields.Char(
        string='PO Customer',
    )
    stock_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Location',
        check_company=True,
        domain=[('usage', '!=', 'view')],
    )
    amount_total = fields.Float(
        string='Amount Total',
        compute='_compute_amount_total',
    )
    user_approve_id = fields.Many2one(
        comodel_name='res.users',
        string='User Approve',
    )
    can_approve = fields.Boolean(
        string='Can Approve',
        compute='_compute_can_approve',
    )
    mrp_ids = fields.Many2many(
        comodel_name='mrp.production',
        string='Production',
        domain="[('state','=','done')]",
    )
#     approval_id = fields.Many2one(
#         comodel_name='approval.request',
#         string='Approval',
#         copy=False,
#     )
    picking_count = fields.Integer(
        string='Picking Count',
        compute='_compute_picking_count',
    )

    def _compute_picking_count(self):
        """docstring for _compute_picking_count"""
        for rec in self:
            picking = self.env['stock.picking'].search([('origin', '=', rec.name)])
            rec.picking_count = len(picking)

    def button_picking_all(self):
        """docstring for button_app_all"""
        obj_search = self.env['stock.picking'].search([('origin', '=', self.name)])
        action = self.sudo().env.ref('stock.action_picking_tree_all').read()[0]
        if len(obj_search) > 1:
            action['domain'] = [('id', 'in', obj_search.ids)]
        elif len(obj_search) == 1:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = obj_search.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.depends('line_ids.product_qty', 'line_ids.unit_price')
    def _compute_amount_total(self):
        """docstring for _compute_amount_total"""
        for rec in self:
            rec.amount_total = sum(line.amount_subtotal for line in rec.line_ids)

    def button_app_all(self):
        """docstring for button_app_all"""
        obj_search = self.approval_id
        action = self.sudo().env.ref('approvals.approval_request_action_all').read()[0]
        if len(obj_search) > 1:
            action['domain'] = [('id', 'in', obj_search.ids)]
        elif len(obj_search) == 1:
            action['views'] = [(self.env.ref('approvals.approval_request_view_form').id, 'form')]
            action['res_id'] = obj_search.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_form(self):
        """docstring for action_view_form"""
        obj_search = self
        action = self.sudo().env.ref('stock_request.stock_request_action').read()[0]
        if len(obj_search) > 1:
            action['domain'] = [('id', 'in', obj_search.ids)]
        elif len(obj_search) == 1:
            action['views'] = [(self.env.ref('stock_request.view_stock_request_form').id, 'form')]
            action['res_id'] = obj_search.id
        else:  
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def _compute_delivered_status(self):
        """docstring for _compute_delivered_status"""
        for rec in self:
            if not rec.picking_id:
                rec.delivered_status = 'No Picking'
            else:
                picking_state = dict(rec.picking_id._fields['state'].selection).get(rec.picking_id.state)
                rec.delivered_status = picking_state

    def _compute_can_approve(self):
        """docstring for _compute_can_approve"""
        for rec in self:
            rec.can_approve = False
            user = self.env.user
            user_access = rec._get_user_by_type()
            if user in user_access:
                rec.can_approve = True

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'state': 'draft',
            'name': self.env['ir.sequence'].with_context(ir_sequence_date=self.date_start).next_by_code('stock.request'),
        })
        return super(StockRequest, self).copy(default)

    @api.model_create_multi
    def create(self, vals):
#         if vals.get('name', 'New') == 'New':
        if isinstance(vals, list) and len(vals) > 0:
            vals = vals[0]

        vals['name'] = self.env['ir.sequence'].with_context(ir_sequence_date=vals.get('date_start')).next_by_code('stock.request') or 'New'

        if vals.get('assigned_to'):
            assigned_to = self.env['res.users'].browse(vals.get(
                'assigned_to'))
            vals['message_follower_ids'] = [(4, assigned_to.partner_id.id)]

#         if len(vals.get('line_ids')) <= 0:
#             raise exceptions.Warning(
#                 _('Choose one or more products line.'))

        return super(StockRequest, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise UserError(_("Please delete in draft or cancel"))
        return super().unlink()

    def _prepare_invoice_line_from_po_line(self, line):
       #if line.product_id.purchase_method == 'purchase':
       #    qty = line.product_qty - line.qty_invoiced
       #else:
       #    qty = line.qty_received - line.qty_invoiced
        qty = line.product_qty
        if float_compare(qty, 0.0, precision_rounding=line.product_uom.rounding) <= 0:
            qty = 0.0
        taxes = line.taxes_id
        invoice_line_tax_ids = line.order_id.fiscal_position_id.map_tax(taxes)
        invoice_line = self.env['account.invoice.line']
        data = {
            'purchase_line_id': line.id,
            'name': line.name,
            'product_uom_id': line.product_uom.id,
            'product_id': line.product_id.id,
            'product_qty': qty,
#             'analytic_account_id': line.account_analytic_id.id,
        }
        return data

    @api.onchange('purchase_ids')
    def _onchange_purchase(self):
        if not self.purchase_ids:
            self.line_ids = None
            return {}
        new_lines = self.env['stock.request.line']
        for purchase in self.purchase_ids:
            for line in purchase.order_line:
                if line.product_id.type == 'service':
                    continue
                data = self._prepare_invoice_line_from_po_line(line)
                if data['product_qty'] == 0:
                    continue
                new_line = new_lines.new(data)
                new_lines += new_line
        self.line_ids = new_lines
        return {}

    def _prepare_stock_line_from_mo(self, line):
        qty = line.qty_producing
        if float_compare(qty, 0.0, precision_rounding=line.product_uom_id.rounding) <= 0:
            qty = 0.0
        data = {
            'name': line.name,
            'product_uom_id': line.product_uom_id.id,
            'product_id': line.product_id.id,
            'product_qty': qty,
        }
        return data

    @api.onchange('mrp_ids')
    def _onchange_mrp(self):
        if not self.mrp_ids:
            self.line_ids = None
            return {}
        new_lines = self.env['stock.request.line']
        for mrp in self.mrp_ids:
            data = self._prepare_stock_line_from_mo(mrp)
            if data['product_qty'] == 0:
                continue
            new_line = new_lines.new(data)
            new_lines += new_line
        self.line_ids = new_lines
        return {}

    def action_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    def _get_user_by_type(self):
        user = None
#         if self.stock_type == 'asset':
#             user = self.env.ref('stock_request.group_stock_request_asset').users
#         elif self.stock_type == 'back_office':
#             user = self.env.ref('stock_request.group_stock_request_back_office').users
#         elif self.stock_type in ('project', 'service'):
#             if not self.director_user_ids:
#                 raise UserError(_("Please Check Director of Employee"))
#             user = self.director_user_ids
#         elif self.stock_type == 'transfer_spare' or self.stock_type == 'sample_product':
#             user = self.env.ref('stock_request.group_stock_request_transfer_spare').users
#         elif self.stock_type == 'production':
#             user = self.env.ref('stock_request.group_stock_request_production').users
        user = self.stock_type_id.user_ids
        return user

    def get_purchase_name(self):
        for rec in self:
            list_purchase_name = ''
            for purchase in self.purchase_ids:
                if list_purchase_name:
                    list_purchase_name += ','
                list_purchase_name += purchase.name
            return list_purchase_name

    def get_partner_list(self):
        for rec in self:
            user_notify = rec._get_user_by_type()
            if user_notify:
                list_partner = ''
                for user in user_notify:
                    if list_partner:
                        list_partner += ','
                    list_partner += str(user.partner_id.id)
                return list_partner

    def _get_user_by_type_stock_picking(self):
        user = None
        if self.stock_type_id != False:
            user = self.env.ref('stock_request.group_stock_request_create_stock_picking').users
        return user

    def get_partner_list_stock_picking(self):
        for rec in self:
            user_notify = rec._get_user_by_type_stock_picking()
            if user_notify:
                list_partner = ''
                for user in user_notify:
                    if list_partner:
                        list_partner += ','
                    list_partner += str(user.partner_id.id)
                return list_partner

    def return_date_schedule_format(self):
        date = self.schedule_date
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
        date_return = datetime.strftime(date, '%e %B %Y %H:%M:%S')
        return date_return

    def return_date_start_format(self):
        date = self.date_start
        date = datetime.strptime(date, '%Y-%m-%d' ) + timedelta(hours=7)
        date_return = datetime.strftime(date, '%e %B %Y ')
        return date_return

    def send_mail(self):
        for rec in self:
            template = False
            if rec.stock_type == 'asset':
                template = self.env.ref('stock_request.stock_request_asset_notify_email')
            elif rec.stock_type == 'back_office':
                template = self.env.ref('stock_request.stock_request_back_office_notify_email')
            elif rec.stock_type == 'service':
                template = self.env.ref('stock_request.stock_request_service_notify_email')
            elif rec.stock_type == 'project':
                template = self.env.ref('stock_request.stock_request_project_notify_email')
            elif rec.stock_type == 'service':
                template = self.env.ref('stock_request.stock_request_service_notify_email')
            elif rec.stock_type == 'transfer_spare':
                template = self.env.ref('stock_request.stock_request_transfer_spare_notify_email')
            if template:
                template.send_mail(
                    rec.id,
                    force_send=True,
                    raise_exception=False
                )

    def send_mail_approve(self):
         for rec in self:
            template = self.env.ref('stock_request.stock_request_approve_notify_email')
            template.send_mail(
                rec.id,
                force_send=True,
                raise_exception=False
            )

    def send_mail_reject(self):
         for rec in self:
            template = self.env.ref('stock_request.stock_request_reject_notify_email')
            template.send_mail(
                rec.id,
                force_send=True,
                raise_exception=False
            )

    def check_approve(self):
        for rec in self:
            if rec.stock_type_id.is_asset_create:
                for line in rec.line_ids:
                    if not line.product_id.asset_category_id:
                        raise UserError(
                            _('Please set asset category of product %s')\
                            % line.product_id.name
                        )
        user = self.env.user
        user_access = self._get_user_by_type()
        if user not in user_access:
            raise UserError(_("You can't Approve"))
        else:
            return True

    def check_cancel(self):
        user = self.env.user
        user_access = self._get_user_by_type()
        if user.id == 2:
            return True
        elif user not in user_access:
            raise UserError(_("You can't Cancel"))
        else:
            return True

    def action_app_reject(self):
        self.button_rejected()

    def action_app_approve(self):
        self.state = 'done'
        self.user_approve_id = self.env.uid
        self.button_create_picking()

    def get_line(self):
        """docstring for get_pr_line"""
        line_prod = []
        for line in self.line_ids:
            line_prod.append((0, 0,{
                'product_id': line.product_id.id if line.product_id else None,
                'description': line.name,
                'quantity': line.product_qty,
                'unit_price': line.unit_price,
            }))
        return line_prod

    def line_update(self, app_id):
        """docstring for get_pr_line"""
        AppProdLine = self.env['approval.product.line']
        for line in self.line_ids:
            AppProdLine.create({
                'approval_request_id': app_id,
                'product_id': line.product_id.id if line.product_id else None,
                'description': line.name,
                'quantity': line.product_qty,
                'unit_price': line.unit_price,
            })

    def create_approval(self):
        """docstring for create_approval"""
        if self.approval_id:
            self.approval_id.product_line_ids.unlink()
            self.approval_id.update({
                'amount': self.amount_total
            })
            self.line_update(self.approval_id.id)
            for app in self.approval_id.approver_ids:
                app.status = 'new'
            approval_id = self.approval_id.id
#             self.approval_id.state = 'new'
        else:
            AppReq = self.env['approval.request']
            cate_obj = self.env['approval.category'].search([('approval_type', '=', 'stock_request')])
            line_prod = self.get_line()
            approver = cate_obj.get_app_pr(self.env.uid, amount=self.amount_total)
            app_obj = AppReq.create({
                'origin': self.name,
                'res_model': 'stock.request',
                'res_id': self.id,
                'request_owner_id': self.env.uid,
                'category_id': cate_obj.id,
                'amount': self.amount_total,
                'date': fields.Datetime.now(),
                'product_line_ids': line_prod,
                'approver_ids': approver,
                'description': self.stock_type_id.name,
            })
            self.approval_id = app_obj.id
            approval_id = app_obj.id
#         app_obj.action_confirm()
        return {
            'name': _("Approval Request"),
            'res_model': 'approval.request',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': approval_id,
        }

    def button_to_approve(self):
#         user = self._get_user_by_type()
        if self.name == 'New':
            self.name = self.env['ir.sequence'].with_context(ir_sequence_date=self.date_start).next_by_code('stock.request')
        if self.stock_type_id.is_approve:
            self.state = 'wait_approve'
        else:
            self.state = 'done'
            self.button_create_picking()
#         self.send_mail()
#         return self.create_approval()
        return True

    def button_approved(self):
        self.check_approve()
        self.state = 'done'
        self.user_approve_id = self.env.uid
        self.button_create_picking()
#         self.send_mail_approve()
        return True

    def button_rejected(self):
        self.state = 'rejected'
#         self.send_mail_reject()
        return True

    def button_cancel(self):
#         self.check_cancel()
        self.state = 'cancel'
        return True

    def _get_stock_move_vals(self, line, picking_id, picking_type_id, dest_location):
        move_val = {
            'name': line.name,
            'date': line.request_id.schedule_date,
            'product_id': line.product_id.id,
            'product_uom_qty': line.product_qty,
            'product_uom': line.product_id.uom_id.id,
            'picking_id': picking_id.id,
            'price_unit': line.product_id.standard_price or 0,
            'location_id': picking_type_id.default_location_src_id.id,
            'location_dest_id': dest_location,
        }
        if self.stock_type_id.is_asset_create:
            move_val.update({'is_asset': True})
        return move_val

    def get_picking_type(self):
        res_company = self.env['res.company'].browse(1)
        picking_type_id = False
        if not self.stock_type_id.picking_type_id:
            raise UserError(
                _('Please set Picking Type in Setting')
            )
        picking_type_id = self.stock_type_id.picking_type_id
#         if self.stock_type == 'asset':
#             if not res_company.asset_picking_type_id:
#                 raise UserError(
#                     _('Please set Asset Picking in configuration')
#                 )
#             picking_type_id = res_company.asset_picking_type_id
#         elif self.stock_type == 'project':
#             if not res_company.project_picking_type_id:
#                 raise UserError(
#                     _('Please set Project Picking in configuration')
#                 )
#             picking_type_id = res_company.project_picking_type_id
#             order_type = 'project_stock_request'
#         elif self.stock_type == 'service':
#             if not res_company.service_picking_type_id:
#                 raise UserError(
#                     _('Please set Service Picking in configuration')
#                 )
#             picking_type_id = res_company.service_picking_type_id
#             order_type = 'service'
#         elif self.stock_type == 'back_office':
#             if not res_company.back_office_picking_type_id:
#                 raise UserError(
#                     _('Please set Back Office Picking in configuration')
#                 )
#             picking_type_id = res_company.back_office_picking_type_id
#             order_type = 'back_office'
#         elif self.stock_type == 'transfer_spare':
#             if not res_company.transfer_spare_picking_type_id:
#                 raise UserError(
#                     _('Please set Transfer Spare Picking in configuration')
#                 )
#             picking_type_id = res_company.transfer_spare_picking_type_id
#         elif self.stock_type == 'production':
#             if not res_company.production_picking_type_id:
#                 raise UserError(
#                     _('Please set Production Picking in configuration')
#                 )
#             picking_type_id = res_company.production_picking_type_id
        return picking_type_id

    def button_create_picking(self):
        for obj in self:
            if not obj.line_ids:
                raise UserError(_('Cannot Create Picking Withdraw without Product.'))
            if not obj.picking_id:
                partner_id = obj.partner_id.id
                dest_location = None
                order_type = None
                picking_type_id = obj.get_picking_type()
                if obj.stock_type_id.stock_location_id:
                    dest_location = obj.stock_type_id.stock_location_id.id
                if obj.stock_location_id:
                    dest_location = obj.stock_location_id.id
                if not dest_location:
                    dest_location = picking_type_id.default_location_dest_id.id

                move_type = 'one'
                group = self.env["procurement.group"].sudo().create({'name': obj.name})

                picking_id = obj.env['stock.picking'].sudo().create({
                    'partner_id': partner_id,
                    'move_type': move_type,
                    'picking_type_id': picking_type_id.id,
                    'location_id': picking_type_id.default_location_src_id.id,
                    'location_dest_id': dest_location,
                    'origin': obj.name,
                    'note': obj.delivery_note,
                    'scheduled_date': obj.schedule_date,
                })

                for line in obj.line_ids:
                    if line.product_qty == 0:
                        continue
#                     if obj.stock_type != 'production':
                    move_val = self._get_stock_move_vals(line, picking_id, picking_type_id, dest_location)
                    if move_val:
#                         if order_type:
#                             move_val.update({'order_type': order_type})
                        move = obj.env['stock.move'].sudo().create(move_val)
#                     else:
#                         if obj.production_id:
#                             mo = obj.production_id
#                             for move_line in mo.move_raw_ids:
#                                 move_line.update({'picking_id': picking_id.id})
                obj.write({'picking_id': picking_id.id})
                picking_id.write({'group_id': group.id})
                picking_id = picking_id
                picking_id.action_confirm()
            else:
                picking_id = obj.picking_id
            return {
                "type": "ir.actions.act_window",
                "res_model": "stock.picking",
                'view_mode': 'form',
                'res_id': picking_id.id,
                "domain": [["id", "in", [picking_id.id]]],
                "context": {"create": False},
                "name": "Picking Withdraw",
            }

    def create_asset(self, list_asset):
        for rec in self:
            if rec.stock_type_id.is_asset_create:
                continue
            Asset_obj = self.env['account.asset.asset']
            for line in list_asset:
                product_id = line['product_id']
                lot_id = line['lot_id']
                asset_exist = Asset_obj.sudo().search([
                    ('product_id', '=', product_id.id),
                    ('stock_request_id', '=', rec.id),
                    ('lot_id', '=', lot_id.id),
                ])
                if not asset_exist:
                    if not product_id.asset_category_id:
                        raise UserError(
                            _('Please set asset category of product %s')\
                            % product_id.name
                        )
                    category = product_id.asset_category_id
                    asset_create = ({
                        'name': product_id.name,
                        'product_id': product_id.id,
                        'category_id': product_id.asset_category_id.id,
                        'caculate_date': line['date'],
                        'value': line['value'],
                        'method': category.method,
                        'method_number': category.method_number,
                        'method_time': category.method_time,
                        'method_period': category.method_period,
                        'method_progress_factor': category.method_progress_factor,
                        'method_end': category.method_end,
                        'prorata': category.prorata,
                        'number_of_year': category.method_number,
                        'number_of_month': category.number_of_month,
                        'begin_price': 0.0,
                        'before_period': 0,
                        'manual_period': 0.0,
                        'stock_request_id': rec.id,
                        'lot_id': lot_id.id,
                        'type': 'purchase',
                        'partner_id': rec.partner_id.id,
                    })
                    asset = Asset_obj.sudo().create(asset_create)

class StockRequestLine(models.Model):

    _name = "stock.request.line"
    _description = "Stock Request Line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    def _get_supplier(self):
        if self.product_id:
            for product_supplier in self.product_id.seller_ids:
                self.supplier_id = product_supplier.name

    @api.depends('product_id', 'name', 'product_uom_id', 'product_qty',
                 'analytic_account_id')
    def _get_is_editable(self):
        for obj in self:
            if obj.request_id.state in ('wait_approve', 'done', 'rejected'):
                obj.is_editable = False
            else:
                obj.is_editable = True

    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])
            for line_rec in first_line_rec.request_id.line_ids:
                line_rec.line_no = line_num
                line_num += 1


    line_no = fields.Integer(
        compute='_get_line_numbers',
        string='Serial Number',
        readonly=False,
        default=False
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[
#             ('purchase_ok', '=', True),
            ('type', '!=', 'service')
        ],
        tracking=True,
    )
    purchase_line_id = fields.Many2one(
        comodel_name='purchase.order.line',
        string='Purchase Line',
    )
    qty_available = fields.Float(
        related="product_id.qty_available",
        string="Qty Onhand",
        required=True,
    )
    name = fields.Text(
        'Description',
        tracking=True,
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        'UOM',
        tracking=True,
    )
    product_qty = fields.Float(
        'Quantity',
        tracking=True,
        digits='Product Unit of Measure',
        required=True,
    )
    request_id = fields.Many2one(
        'stock.request',
        'Purchase Request',
        ondelete='cascade',
        readonly=True
    )
    company_id = fields.Many2one(
        'res.company',
        related='request_id.company_id',
        string='Company',
        store=True,
        readonly=True
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        'Analytic Account',
        tracking=True,
        required=False,
    )
    requested_by = fields.Many2one(
        'res.users',
        related='request_id.requested_by',
        string='Requested by',
        store=True,
        readonly=True
    )
    assigned_to = fields.Many2one(
        'res.users',
        related='request_id.assigned_to',
        string='Assigned to',
        store=True,
        readonly=True
    )
    description = fields.Text(
        related='request_id.description',
        string='Description',
        readonly=True,
        store=True
    )
    origin = fields.Char(
        related='request_id.origin',
        size=32,
        string='Source Document',
        readonly=True,
        store=True
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        related='request_id.warehouse_id',
        string='Warehouse',
        store=True,
        readonly=True
    )
    supplier_id = fields.Many2one(
        'res.partner',
        string='Preferred supplier',
        compute="_get_supplier"
    )
    customer_name = fields.Char(
        'Customer name',
        size=256,
    )
    unit_price = fields.Float(
        string='Unit Price',
        digits='Product Price',
        readonly=False,
    )
    amount_subtotal = fields.Float(
        string='Amount Subtotal',
        compute='_compute_subtotal',
    )
    is_editable = fields.Boolean(
        string='Is editable',
        compute="_get_is_editable",
        readonly=True
    )

    @api.depends('unit_price', 'product_qty')
    def _compute_subtotal(self):
        """docstring for _compute_subtotal"""
        for rec in self:
            rec.amount_subtotal = rec.unit_price * rec.product_qty

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.default_code:
                name = '[%s] %s' % (self.product_id.default_code, name)
            if self.product_id.description_purchase:
                name += '\n' + self.product_id.description_purchase
            self.name = name
            #self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.product_uom_id = self.product_id.uom_id.id
            self.unit_price = self.product_id.standard_price



class StockRequestRemine(models.Model):
    _name = 'stock.request.remine'
    _description = "Stock Request Remind"

    request_id = fields.Many2one(
        comodel_name="stock.request",
        string="Stock Request",
        required=False,
    )
    desc = fields.Char(
        string="Desc",
        required=True,
    )
    date_remine = fields.Date(
        string="Date Remind",
        required=True,
    )
    amount = fields.Float(
        string="Amount",
        required=True,
    )
    state = fields.Selection(
        string="state",
        selection=[
           ('wait', 'Wait'),
           ('done', 'Done'),
        ],
        required=False,
        default='wait',
    )

