# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from shopee_connector.auth import Auth
from shopee_connector.api.product import Product
from shopee_connector.api.logistic import Logistic


class ShopeeSetting(Document):
	def after_insert(self):
		# pass
		data = Auth.test_token(self.seller_test,self.shop_id,self.partner_id,self.key,self.code)
		self.refresh_token = data['refresh_token']
		self.access_token = data['access_token']
		

	def validate(self):
		# pass
		# data = Auth.test_token(self.seller_test,self.shop_id,self.partner_id,self.key,self.code)
		# frappe.msgprint(str(data))
		# Auth.test_token(self.seller_test,self.shop_id,self.partner_id,self.key,self.code)
		# self.gen_t_rt()
		Auth.test_toko(self.seller_test,self.shop_id,self.partner_id,self.key,self.access_token)
		# Product.get_category(self.seller_test,self.access_token,self.partner_id,self.key,self.shop_id)

	@frappe.whitelist()
	def gen_url(self):
		self.url = Auth.test_auth(self.seller_test,self.partner_id,self.key)
		# self.save()

	@frappe.whitelist()
	def gen_t_rt(self):
		data = Auth.gen_token_rt(self.seller_test,self.shop_id,self.partner_id,self.key,self.refresh_token)
		frappe.msgprint(str(data))
		frappe.msgprint(data['refresh_token'])
		frappe.msgprint(data['access_token'])
		# self.refresh_token = data['refresh_token']
		self.access_token = data['access_token']
		self.new_refresh_token = data['refresh_token']
		self.save()

	@frappe.whitelist()
	def get_auth_code(self):
		Auth.test_token(self.seller_test,self.shop_id,self.partner_id,self.key,self.code)

	@frappe.whitelist()
	def gen_t_c(self):
		Auth.gen_token_code(self.seller_test,self.partner_id,self.key,self.code)

	@frappe.whitelist()
	def get_logistic(self):
		Logistic.get_channel_list(self.seller_test,self.access_token,self.partner_id,self.key,self.shop_id)