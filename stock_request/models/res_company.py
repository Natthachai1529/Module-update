# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    asset_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Asset Picking',
    )
    project_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Project Picking',
    )
    service_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Service Picking',
    )
    back_office_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Back Office Picking',
    )
    transfer_spare_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Transfer Spare Picking',
    )
    production_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Production Picking',
    )
