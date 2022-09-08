# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ShopeeFakeStock(Document):
	def validate(self):
		self.update_stock()

	@frappe.whitelist()
	def update_stock(self):
		if self.type == "Product":
			
			doc = frappe.get_doc("Item Shopee",self.item_shopee)
			doc.stock = self.stock
			doc.is_fake = 1
			doc.flags.ignore_permission = True
			doc.save()

		if self.type == "Template":
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
