# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    is_require_lot = fields.Boolean(
        string='Required Lot',
    )

class AccountAsset(models.Model):
    _inherit = 'account.asset.asset'

    stock_request_id = fields.Many2one(
        comodel_name='stock.request',
        string='Stock Request',
    )
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lots/Serial',
    )
    is_require_lot = fields.Boolean(
        string='Required Lot',
        related='category_id.is_require_lot',
    )


