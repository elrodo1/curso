# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models

class res_partner(models.Model):
    
    _inherit='res.partner'
    
    instructor = fields.Boolean('Es Instructor', default=False)
