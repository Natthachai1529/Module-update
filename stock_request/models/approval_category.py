# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    approval_type = fields.Selection(
        selection_add=[
            ('stock_request', 'Stock Request'),
        ]
    )
