# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for rec in self:
            if rec.origin and rec.origin.startswith('SR'):
                sr = self.env['stock.request'].search([('picking_id', '=', rec.id)])
                department_id = sr.requested_by.department_id
                if sr.stock_type_id.is_depart_acc:
                    acc = sr.stock_type_id.get_acc_by_department(department_id.id)
                    if not acc:
                        raise UserError(_('Please set account for department %s' % department_id.name))
                    for move in rec.move_ids_without_package:
                        for svl in move.stock_valuation_layer_ids:
                            prod_acc = svl.product_id._get_product_accounts()
                            stock_output = prod_acc['stock_output']
                            acc_move = svl.account_move_id
                            for mv_line in acc_move.line_ids:
                                if mv_line.account_id == stock_output:
                                    mv_line.update({'account_id': acc})
        return res
