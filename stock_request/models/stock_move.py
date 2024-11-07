# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class Move(models.Model):
    _inherit = 'stock.move'

    is_asset = fields.Boolean(
        string='Is Asset?',
        default=False,
    )
#     order_type_id = fields.Many2one(
#         comodel_name='account.order.type',
#         string='Order Type',
#     )
    order_type = fields.Selection(
        selection=[
            ('new', 'New Product'),
            ('refurbished', 'Refurbished'),
            ('percall', 'Per Call'),
            ('rent', 'Rent'),
            ('ma', 'MA'),
            ('outsource', 'Outsource'),
            ('service', 'Service'),
            ('project', 'Project'),
            ('project_stock_request', 'Project Stock Request'),
            ('project_outsource', 'Project Outsource'),
            ('project_utility', 'Project Utility'),
            ('back_office', 'Back Office'),
        ],
        string='Order Type',
    )

    def _get_accounting_data_for_valuation(self):
        journal_id, acc_src, acc_dest, acc_valuation = super(Move, self)._get_accounting_data_for_valuation()
        if self.is_asset:
            if not self.product_id.asset_category_id:
                raise UserError(
                    _('Please set asset category of product %s')\
                    % self.product_id.name
                )
            acc_dest = self.product_id.asset_category_id.account_asset_id.id
#         if self.order_type_id:
#             order_type_obj = self.order_type_id
#             prod_categ = self.product_id.categ_id
#             if self.picking_id.picking_type_code == 'outgoing':
#                 acc_src = order_type_obj.account_expense_id.id
#             elif self.picking_id.picking_type_code == 'internal':
#                 acc_dest = order_type_obj.account_expense_id.id
        return journal_id, acc_src, acc_dest, acc_valuation
