# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, api,fields
from odoo.tools import pycompat
from odoo.tools.float_utils import float_round


class ExportCustomerPricelistReport(models.AbstractModel):
	_name = 'report.export_customer_pricelist_app.report_exportcustomerinfo' 
	_description = 'Customer Pricelist Report'

	def _get_customer_details(self, partner):
		lines =[]
		product_ids = self.env['product.product'].search([])
		pricelist_id = partner.property_product_pricelist
		for product in product_ids:
			value  = {}
			customer_price = pricelist_id._compute_price_rule(
									[(product, 1.0, partner)], date=fields.Date.today(), uom_id=product.uom_id.id)[product.id][0]
			price_discount = 0.0
			if product.list_price > customer_price:
				price_discount = product.list_price - customer_price
				price_discount = (100 * (price_discount))/product.list_price
			else:
				price_discount = 0.0
			value.update({
				'product_id'         : product.id,
				'product_name'       : product.name or '',
				'product_code'       : product.default_code or '',
				'product_barcode'	 : product.barcode or '',
				'public_price'		 : product.lst_price or 0.0,
				'price_discount'	 : price_discount or 0.0,
				'customer_price'	 : customer_price or 0.0,
			}) 
			lines.append(value)
		return lines

	@api.model
	def _get_report_values(self, docids, data=None):
		partner_ids = self.env['res.partner'].browse(data['form']['partner_ids'])
		docargs = {
				   'doc_model': 'export.customer.pricelist',
				   'data': data,
				   'docs': partner_ids,
				   'get_customer_details':self._get_customer_details
				   }
		return docargs