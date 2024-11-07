# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockRequestWizard(models.TransientModel):

    _name = 'stock.request.wizard'
    _description = "Stock Request Wizard"

    line_ids = fields.One2many(
        comodel_name='stock.request.wizard.line',
        inverse_name='wizard_id',
        string='Wizard',
        help='Help note'
    )

    @api.model
    def _prepare_item(self, line):
        print
        return {
            'product_id': line.product_id.id,
            'product_qty': line.product_qty,
            'qty_available': line.qty_available,
            'stock_qty': 0,
        }

    @api.model
    def default_get(self, fields):
        res = super(StockRequestWizard, self).default_get(fields)
        request_line_obj = self.env['stock.request.line']
        request_line_ids = self.env.context['active_ids'] or []
        active_model = self.env.context['active_model']
        request_obj = self.env[active_model].browse(request_line_ids)

        if not request_line_ids:
            return res

        items = []
        for line in request_obj.line_ids:
                items.append([0, 0, self._prepare_item(line)])
        res['line_ids'] = items
        return res


class StockRequesWizardLine(models.TransientModel):

    _name = 'stock.request.wizard.line'
    _description = "Stock Request Wizard Line"

    wizard_id = fields.Many2one(
        comodel_name='stock.request.wizard',
        string='Wizard',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
    )
    product_qty = fields.Float(
        string='Quantity',
    )
    qty_available = fields.Float(
        string='Qty Onhand',
        related='product_id.qty_available',
    )
    stock_qty = fields.Float(
        'Stock QTY',
    )
