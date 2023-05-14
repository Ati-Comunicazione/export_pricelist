# -*- coding: utf-8 -*-

import os
from odoo import fields, models, api, _
from datetime import datetime
import xlsxwriter
import base64
import io
from io import BytesIO
import tempfile
import csv
from io import StringIO
from odoo.exceptions import UserError, ValidationError

class ExportCustomerPricelist(models.TransientModel):
	_name = 'export.customer.pricelist'
	_description = 'Customer Pricelist Report'
	
	partner_ids = fields.Many2many('res.partner', string="Customer")

	file=fields.Binary("Download File")
	file_name = fields.Char(string="File Name")
	file_type = fields.Selection([('pdf', 'PDF'),('csv', 'CSV'),('xls', 'XLS')
								],'File Type', default="pdf")

	def customer_pricelist_xls(self):
		if self.file_type == 'pdf':
			self.ensure_one()
			[data] = self.read()
			item_ids = data.get('partner_ids')
			for item in item_ids:
				partner = self.env['res.partner'].browse(item)
				if not partner.property_product_pricelist.item_ids:
					raise ValidationError(_("No Price Rules Define for the selected Pricelist"))
			datas = {
				 'ids': [1],
				 'model': 'export.customer.pricelist',
				 'form': data
			}
			return self.env.ref('export_customer_pricelist_app.action_report_export_customer_pricelist').report_action(self, data=datas)
		elif self.file_type == 'xls':
			name_of_file = 'Export Customer Pricelist.xls'
			file_path = 'Export Customer Pricelist' + '.xls'
			workbook = xlsxwriter.Workbook('/tmp/'+file_path)
			worksheet = workbook.add_worksheet('Export Customer Pricelist')
			
			header_format = workbook.add_format({'bold': True,'valign':'vcenter','font_size':16,'align': 'center','bg_color':'#D8D8D8'})
			title_format = workbook.add_format({'border': 1,'bold': True, 'valign': 'vcenter','align': 'center', 'font_size':14,'bg_color':'#D8D8D8'})
			cell_wrap_format_bold = workbook.add_format({'border': 1, 'bold': True,'valign':'vjustify','valign':'vcenter','align': 'center','font_size':12,'bg_color':'#D8D8D8'}) ##E6E6E6
			cell_wrap_format = workbook.add_format({'border': 1,'valign':'vjustify','valign':'vcenter','align': 'left','font_size':12,}) ##E6E6E6

			worksheet.set_row(1,20)  #Set row height
			#Merge Row Columns
			TITLEHEDER = 'Export Customer Pricelist' 

			worksheet.set_column(0, 0, 20)
			worksheet.set_column(1, 6, 25)

			partner_ids = self.env['res.partner'].browse(self.partner_ids.ids)

			worksheet.merge_range(1, 0, 1, 6, TITLEHEDER,header_format)
			rowscol = 1
			for partner in partner_ids:
				if partner.property_product_pricelist:
					worksheet.merge_range(rowscol + 2, 0, rowscol + 2, 6, str(partner.name), title_format)
					rowscol = rowscol + 2
					pricelist_id = partner.property_product_pricelist
					worksheet.write(rowscol + 2, 0, 'Product Id', cell_wrap_format_bold)
					worksheet.write(rowscol + 2, 1, 'Product Name', cell_wrap_format_bold)
					worksheet.write(rowscol + 2, 2, 'Product Code',cell_wrap_format_bold)
					worksheet.write(rowscol + 2, 3, 'Barcode', cell_wrap_format_bold)
					worksheet.write(rowscol + 2, 4, 'Public Price', cell_wrap_format_bold)
					worksheet.write(rowscol + 2, 5, 'Discount', cell_wrap_format_bold)
					worksheet.write(rowscol + 2, 6, 'Customer Price', cell_wrap_format_bold)
					product_ids = self.env['product.product'].search([])
					rows = (rowscol + 3)
					for product in product_ids:
						worksheet.write(rows, 0, product.id, cell_wrap_format)
						worksheet.write(rows, 1, product.name or '', cell_wrap_format)
						worksheet.write(rows, 2, product.default_code or '', cell_wrap_format)

						if product.barcode == False:
							worksheet.write(rows, 3,'',cell_wrap_format)
						else:
							worksheet.write(rows, 3, product.barcode, cell_wrap_format)

						lst_price = ('%.2f'% float(product.lst_price or 0.0))
						worksheet.write(rows, 4, str(lst_price or 0.0) ,cell_wrap_format)
						# Pricelist Calculation
						customer_price = pricelist_id._compute_price_rule(
												[(product, 1.0, partner)], date=fields.Date.today(), uom_id=product.uom_id.id)[product.id][0]
						price_discount = 0.0
						if product.list_price > customer_price:
							price_discount = product.list_price - customer_price
							price_discount = (100 * (price_discount))/product.list_price
						else:
							price_discount = 0.0
						worksheet.write(rows, 5,str(price_discount), cell_wrap_format)
						worksheet.write(rows, 6,str(customer_price), cell_wrap_format)
						rows = rows + 1
					rowscol = rows
				rowscol = rowscol

			workbook.close()
			export_id = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())
			result_id = self.env['export.customer.pricelist'].create({'file': export_id ,'file_name': name_of_file})
			return {
					'name': 'Export Customer Pricelist',
					'view_mode': 'form',
					'res_id': result_id.id,
					'res_model': 'export.customer.pricelist',
					'view_type': 'form',
					'type': 'ir.actions.act_window',
					'target': 'new',
				}

		elif self.file_type == 'csv':
			file_path = 'Export Customer Pricelist.csv'
			workbook = xlsxwriter.Workbook('/tmp/'+file_path)
			with open('/tmp/Export Customer Pricelist.csv', 'w', newline='') as csvFile:
				writer = csv.writer(csvFile)
				partner_ids = self.env['res.partner'].browse(self.partner_ids.ids)
				writer.writerow('')
				TITLEHEDER = ['','','Export Customer Pricelist']
				writer.writerow(TITLEHEDER)
				writer.writerow('')
				for partner in partner_ids:
					if not partner.property_product_pricelist.item_ids:
						raise ValidationError(_("No Price Rules Define for the selected Pricelist"))
					partner_name = ['','',str(partner.name)]
					writer.writerow(partner_name)
					writer.writerow('')
					header = ['Product ID','Product Name','Product Code',   'Barcode'    ,'Price','Discount','Customer Price']
					writer.writerow(header)
					product_ids = self.env['product.product'].search([])
					pricelist_id = partner.property_product_pricelist
					for product in product_ids:
						product_value = [[str(product.id),str(product.name)]]
						if product.default_code == False:
							product_value[0].append(None)
						else:
							product_value[0].append(str(product.default_code))
						if product.barcode == False:
							product_value[0].append(None)
						else:
							product_value[0].append(str(product.barcode))
						product_value[0].append(str(product.lst_price or 0.0))
						# Pricelist Calculation
						customer_price = pricelist_id._compute_price_rule(
												[(product, 1.0, partner)], date=fields.Date.today(), uom_id=product.uom_id.id)[product.id][0]
						price_discount = 0.0
						if product.list_price > customer_price:
							price_discount = product.list_price - customer_price
							price_discount = (100 * (price_discount))/product.list_price
						else:
							price_discount = 0.0
						product_value[0].append(str(price_discount))
						product_value[0].append(str(customer_price))
						writer.writerows(product_value)
					new_line = '\n'
					writer.writerows(new_line)
			csvFile.close()
			export_id = base64.b64encode(open('/tmp/Export Customer Pricelist.csv' , 'rb+').read())
			result_id = self.env['export.customer.pricelist'].create({'file': export_id ,'file_name': file_path})
			return {
					'name': 'Export Customer Pricelist',
					'view_mode': 'form',
					'res_id': result_id.id,
					'res_model': 'export.customer.pricelist',
					'view_type': 'form',
					'type': 'ir.actions.act_window',
					'target': 'new',
				}
		else:
			raise UserError(_('Please Select File Type To Continue.'))


	def send_by_mail_customer_pricelist(self):
		[data] = self.read()
		datas = {
				 'ids': [1],
				 'model': 'export.customer.pricelist',
				 'form': data
		}
		for partner in self.partner_ids:
			datas['form']['partner_ids'] = partner.id
			template_id = self.env['ir.model.data'].get_object_reference('export_customer_pricelist_app','email_template_customer_pricelist')[1]
			email_template_obj = self.env['mail.template'].browse(template_id)
			if template_id:
				values = email_template_obj.generate_email(self.id, fields=None)
				values['email_from'] = self.env.user.email
				values['email_to'] = partner.email
				values['author_id'] = self.env.user.partner_id.id
				values['res_id'] = False
				pdf = self.env.ref('export_customer_pricelist_app.action_report_export_customer_pricelist').render_qweb_pdf(self.id,data=datas)[0]
				values['attachment_ids'] = [(0,0,{
					'name': 'Export Customer Pricelist Report',
					'datas': base64.b64encode(pdf),
					'res_model': 'export.customer.pricelist',
					'res_id': self.id,
					'mimetype': 'application/x-pdf',
					'type': 'binary',
					})]
				mail_mail_obj = self.env['mail.mail']
				msg_id = mail_mail_obj.sudo().create(values)
				if msg_id:
					msg_id.sudo().send()
