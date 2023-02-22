# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from shopee_connector.api.product import add_item_erp_to_shopee, update_item_erp_to_shopee, add_item_variant_erp_to_shopee, update_item_variant_erp_to_shopee, get_item_base_info, get_model_list, update_stock_item_api
import json

class ShopeeFakeStock(Document):
	def validate(self):
		self.update_stock()

	@frappe.whitelist()
	def update_stock(self):
		if self.type == "Product":
			shopeesetting = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE name = '{}' """.format(self.shop),as_dict=1)
			for i in shopeesetting:
				saller_test = i['seller_test']
				acces_token = i['access_token']
				partner_id = i['partner_id']
				key = i['key']
				shop_id = i['shop_id']

			payloadUpdate = {
				"item_id":int(self.item_id),
				"stock_list": [
					{
					"model_id": 0,
					"seller_stock": [
						{
						"location_id": "",
						"stock": self.stock
						}
					]
					},
				]
			}
			dataPayload2 = json.dumps(payloadUpdate)
			# frappe.throw(str(dataPayload))
			frappe.msgprint(str(dataPayload2))			
			test = update_stock_item_api(saller_test,acces_token,partner_id,key,shop_id,payloadUpdate)
			frappe.msgprint(str(test)+'TEST XX')

			doc = frappe.get_doc("Item Shopee",self.item_shopee)
			doc.stock = self.stock
			doc.is_fake = 1
			doc.flags.ignore_permission = True
			doc.save()

		if self.type == "Template":
			stock_list = []
			shopeesetting = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE name = '{}' """.format(self.shop),as_dict=1)
			for i in shopeesetting:
				saller_test = i['seller_test']
				acces_token = i['access_token']
				partner_id = i['partner_id']
				key = i['key']
				shop_id = i['shop_id']


			for ivf in self.item_shopee_variant_fake:								
				tempDict = {
					"model_id" : int(ivf.model_id),
					"seller_stock" : [
						{
							"location_id": "",
							"stock": ivf.stock
						}
					]
				}
				stock_list.append(tempDict)

			payloadUpdate = {
				"item_id":int(self.item_id),
				"stock_list":stock_list
			}

			dataPayload2 = json.dumps(payloadUpdate)
			# frappe.throw(str(dataPayload))
			frappe.msgprint(str(dataPayload2))	
			update_stock_item_api(saller_test,acces_token,partner_id,key,shop_id,payloadUpdate)

			doc = frappe.get_doc("Item Shopee",self.item_shopee)
			for ivf in self.item_shopee_variant_fake:
				conter=0
				for tgv in doc.variation_table:
					if ivf.stock > 0 :
						if ivf.model_id == tgv.model_id:
							tgv.is_fake = 1
							tgv.stock = ivf.stock
							tgv.tfs = self.name
		
			doc.flags.ignore_permissions = True
			doc.save()

	
@frappe.whitelist()
def ambil_variant(item_shopee):
	# self.marketplace_item_tokopedia
	data = frappe.db.sql(""" SELECT * from `tabTable Variation` where parent='{}' ORDER BY idx ASC """.format(item_shopee),as_dict=1)

	return data
