# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StockRequestType(models.Model):
    _name = 'stock.request.type'
    _description = 'Stock.request.type'
    _order = 'sequence, id'

    name = fields.Char(
        string='Name Type',
        required=True,
    )
    sequence = fields.Integer(
        string='Seq',
        default=10,
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        default=lambda self: self.env.company,
    )
#     order_type_id = fields.Many2one(
#         comodel_name='account.order.type',
#         string='Order Type',
#         required=True,
#     )
    picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Picking Type',
        required=True,
    )
    is_asset_create = fields.Boolean(
        string='Create Asset',
        default=False,
    )
    is_production = fields.Boolean(
        string='MRP Production',
        default=False,
    )
    is_rm = fields.Boolean(
        string='Request Raw Material',
        default=False,
    )
    is_approve = fields.Boolean(
        string='Request Approve',
        default=False,
    )
    default_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Default Partner',
    )
    stock_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Destination Location',
    )
    user_ids = fields.Many2many(
        comodel_name='res.users',
        string='User Approve',
    )
    user_approve_ids = fields.One2many(
        comodel_name='stock.request.type.approver',
        inverse_name='type_id',
        string='Approver',
    )
    is_depart_acc = fields.Boolean(
        string='Department Account Set',
    )
    acc_ids = fields.One2many(
        comodel_name='stock.request.type.account',
        inverse_name='type_id',
        string='Acc List',
    )

    def get_acc_by_department(self, department):
        """docstring for get_acc_by_department"""
        for rec in self:
            acc_id = False
            if rec.is_depart_acc:
                for line in rec.acc_ids:
                    if department == line.deparment_id.id:
                        acc_id = line.account_id.id
            return acc_id


class StockRequestTypeAccount(models.Model):
    _name = 'stock.request.type.account'
    _description = 'Stock Request Type Account'

    type_id = fields.Many2one(
        comodel_name='stock.request.type',
        string='Type',
    )
    deparment_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Stock Output Account',
    )

class StockRequestTypeApprover(models.Model):
    _name = 'stock.request.type.approver'
    _description = 'stock request type approver'

    type_id = fields.Many2one(
        comodel_name='stock.request.type',
        string='Type',
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Users',
    )
