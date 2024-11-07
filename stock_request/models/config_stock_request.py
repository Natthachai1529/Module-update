# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    asset_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Asset Picking',
        related='company_id.asset_picking_type_id',
        readonly=False,
    )
    project_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Project Picking',
        related='company_id.project_picking_type_id',
        readonly=False,
    )
    service_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Service Picking',
        related='company_id.service_picking_type_id',
        readonly=False,
    )
    back_office_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Back Office Picking',
        related='company_id.back_office_picking_type_id',
        readonly=False,
    )
    transfer_spare_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Transfer Spare Picking',
        related='company_id.transfer_spare_picking_type_id',
        readonly=False,
    )
    production_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Production Picking',
        related='company_id.production_picking_type_id',
        readonly=False,
    )

