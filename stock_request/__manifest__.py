# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "BST :: Stock Request",
    "author": "BST",
    "version": "18.0.1.0.0",
    "summary": "Stock",
    "website": "",
    "description": """

    This module for Stock Request.
    ===========================================================


    """,
    "category": "Stock",
    "depends": [
        'base',
        'stock',
        'purchase',
        'project',
        'account',
        'hr',
        'stock_account',
        'mrp',
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/stock_request.xml',
        'data/stock_request_sequence.xml',
#         'data/mail_template.xml',
        'wizard/stock_request_wizard_view.xml',
        'wizard/stock_purchase_wizard_view.xml',
        'wizard/stock_request_cancel_wizard.xml',
        'views/stock_request_view.xml',
        'views/stock_request_type_view.xml',
#         'views/account_asset_view.xml',
        'views/config_view.xml',
    ],
    # "demo": ["demo/purchase_request_demo.xml"],
    "license": "AGPL-3",
    "installable": True,
    "application": True,
}



# {
#     "name": "BST :: Stock Request",
#     "summary": "Stock",
#     "version": "10.0.1.0.0",
#     "category": "Stock",
#     "description": """
#
# This module for Stock Request.
# ===========================================================
#
#
#     """,
#     "website": "",
#     "author": "BST",
#     "license": "AGPL-3",
#     "application": True,
#     "installable": True,
#     "external_dependencies": {
#         "python": [],
#         "bin": [],
#     },
#     "depends": [
#         'base',
#         'stock',
#         'purchase',
#         'project',
#         'account',
#         'hr',
#         'stock_account',
# #         'tat_order_type',
# #         'approvals',
#     ],
#     'data': [
#         'security/ir.model.access.csv',
#         'security/stock_request.xml',
#         'data/stock_request_sequence.xml',
# #         'data/mail_template.xml',
#         'wizard/stock_request_wizard_view.xml',
#         'wizard/stock_purchase_wizard_view.xml',
#         'wizard/stock_request_cancel_wizard.xml',
#         'views/stock_request_view.xml',
#         'views/stock_request_type_view.xml',
# #         'views/account_asset_view.xml',
#         'views/config_view.xml',
#     ],
# }
