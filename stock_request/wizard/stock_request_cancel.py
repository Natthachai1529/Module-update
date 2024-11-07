# -*- coding: utf-8 -*-

from odoo import api, fields, models

class CancelReason(models.TransientModel):
    _name = 'cancel.stock.request'
    _description = 'Cancel Stock Request'

    cancel_stock_request = fields.Char(
        'Cancel Stock Request',
    )
    reject_stock_request = fields.Char(
        'Reject Stock Request',
    )

    def action_cancel_stock_request(self):
        if ('active_model' in self._context and self._context.get('active_model')) and ('active_id' in self._context and self._context.get('active_id')):
            res_model = self._context.get('active_model')
            res_id = self._context.get('active_id')
            model_obj = self.env[res_model].browse(res_id)
            if self.cancel_stock_request:
                model_obj.write({'cancel_reason': self.cancel_stock_request})
                return model_obj.button_cancel()

    def action_reject_stock_request(self):
        if ('active_model' in self._context and self._context.get('active_model')) and ('active_id' in self._context and self._context.get('active_id')):
            res_model = self._context.get('active_model')
            res_id = self._context.get('active_id')
            model_obj = self.env[res_model].browse(res_id)
            if self.reject_stock_request:
                model_obj.write({'reject_reason': self.reject_stock_request})
                return model_obj.button_rejected()
