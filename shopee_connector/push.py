import hmac
import hashlib
import json
import os
import requests
import time

import frappe
import datetime
from datetime import date
# from datetime import datetime, date

from frappe.utils import nowdate, add_days, random_string, get_url
from shopee_connector.api.order import get_order_detail
from shopee_connector.api.order import make_so
from shopee_connector.api.order import make_dn
from shopee_connector.api.payment import get_escrow_detail
from shopee_connector.api.logistic import get_tracking_number
from shopee_connector.shopee_connector.doctype.item_shopee.item_shopee import ItemShopee
from shopee_connector.api.product import add_item_erp_to_shopee, update_item_erp_to_shopee, add_item_variant_erp_to_shopee, update_item_variant_erp_to_shopee, get_item_base_info, get_model_list, update_stock_item_api


# @frappe.whitelist(allow_guest=True)
@frappe.whitelist(allow_guest=True)
def order_status_push():
	tmp = json.loads(frappe.request.data)
	doc_t = frappe.new_doc('Log Shopee')
	doc_t.data = """ {} """.format(tmp)
	# reserved_stock_change_push
	if tmp['code'] == 8:
		doc_t.save(ignore_permissions=True)

	# order_trackingno_push
	elif tmp['code'] == 4:
		doc_t.save(ignore_permissions=True)
		doc_os = frappe.get_doc("Shopee Order",tmp['data']['ordersn'])
		doc_os.tracking_no = tmp['data']['tracking_no']
		doc_os.save(ignore_permissions=True)

	# shop_authorization_push
	elif tmp['code'] == 1:
		doc_t.save(ignore_permissions=True)

	# shipping_carrier_update
	elif tmp['code'] == 14:
		doc_t.save(ignore_permissions=True)
	
	# order_status_push
	elif tmp['code'] == 3:
		shop = frappe.get_doc("Shopee Setting",{'shop_id':tmp['shop_id']}).name
		order = get_order_detail(shop,tmp['data']['ordersn'])
		print(order)
		doc_t.order_detail = str(order)
		doc_t.save(ignore_permissions=True)
		order_sn = tmp['data']['ordersn']
		cust = frappe.get_value("Customer",order['response']['order_list'][0]['buyer_username'], "name")
		if cust:
			frappe.msgprint(order['response']['order_list'][0]['buyer_username']+" sudah ada")
		else:
			docc = frappe.new_doc('Customer')
			docc.customer_name = order['response']['order_list'][0]['buyer_username']
			docc.customer_type = 'Individual'

			docc.flags.ignore_permissions=True
			docc.save()
			frappe.msgprint("Make Customer"+order['response']['order_list'][0]['buyer_username'])

		if frappe.db.exists("Shopee Order",str(order_sn)):
			doc = frappe.get_doc("Shopee Order",order_sn)
			doc.order_status = order['response']['order_list'][0]['order_status']
			os = order['response']['order_list'][0]['order_status']
			it_id = order['response']['order_list'][0]['item_list'][0]['item_id']
			# model_id = order['response']['order_list'][0]['item_list'][0]['model_id']
			cek_shop_p = frappe.get_value("Item Shopee",{'item_id':it_id}, "shopee_setting")
			doc.shopee_setting = cek_shop_p

			# if os == "READY_TO_SHIP":
			# 	make_so(order_sn)
			# 	make_dn(order_sn)

			doc.customer = order['response']['order_list'][0]['buyer_username']
			ct = order['response']['order_list'][0]['create_time']
			doc.create_time = datetime.datetime.fromtimestamp(ct)
			doc.shopee_order_item=[]
			tmp = []
			tmp_a = []
			for it in order['response']['order_list'][0]['item_list']:
				row = doc.append("shopee_order_item",{})
				frappe.msgprint(str(it['model_id'])+"model_id_123aaaa2")
				if it['model_id'] == 0:
					item_code = frappe.get_value("Item Shopee",{'item_id':it['item_id']}, "item_code")
					row.item_code = item_code
				else:
					item_code_var = frappe.get_value("Table Variation",{'model_id':str(it['model_id'])}, "item_code")
					row.item_code = item_code_var

				row.item_id = it['item_id']
				row.item_name = it['item_name']
				row.item_sku = it['item_sku']
				row.model_id = it['model_id']
				row.model_name = it['model_name']
				row.model_sku = it['model_sku']
				row.model_quantity_purchased = it['model_quantity_purchased']
				row.model_discounted_price = it['model_discounted_price']
				row.amount = it['model_quantity_purchased'] * it['model_discounted_price']
				tmp.append(it['weight'] * it['model_quantity_purchased'])
				tmp_a.append(it['model_quantity_purchased'] * it['model_discounted_price'])
			# frappe.msgprint(str(tmp)+"220818EKQDBS20")
			doc.total_orders = sum(tmp_a)
			doc.total_wight = sum(tmp)
			doc.actual_shipping_fee = order['response']['order_list'][0]['actual_shipping_fee']
			doc.estimated_shipping_fee = order['response']['order_list'][0]['estimated_shipping_fee']
			
			if order['response']['order_list'][0]['actual_shipping_fee'] == 0:
				total_sales = sum(tmp_a) + order['response']['order_list'][0]['estimated_shipping_fee']
				doc.total_sales = total_sales
			else:
				total_sales = sum(tmp_a) + order['response']['order_list'][0]['estimated_shipping_fee']
				doc.total_sales = sum(tmp_a) + total_sales
			
			if doc.payment_method == "Indomaret":
				doc.buyer_transaction_fee = 2500
			elif doc.payment_method == "Alfamart":
				doc.buyer_transaction_fee = 2500
			elif doc.payment_method == "COD":
				doc.buyer_transaction_fee = total_sales * 3/100

			doc.total_amount = order['response']['order_list'][0]['total_amount']
			doc.shipping_carrier = order['response']['order_list'][0]['shipping_carrier']
			doc.estimated_shipping_fee = order['response']['order_list'][0]['estimated_shipping_fee']
			doc.package_number = order['response']['order_list'][0]['package_list'][0]['package_number']
			doc.payment_method = order['response']['order_list'][0]['payment_method']
			doc.recipient_name = order['response']['order_list'][0]['recipient_address']['name']
			doc.phone = order['response']['order_list'][0]['recipient_address']['phone']
			doc.district = order['response']['order_list'][0]['recipient_address']['district']
			doc.city = order['response']['order_list'][0]['recipient_address']['city']
			doc.state = order['response']['order_list'][0]['recipient_address']['state']
			doc.zipcode = order['response']['order_list'][0]['recipient_address']['zipcode']
			doc.full_address = order['response']['order_list'][0]['recipient_address']['full_address']
			if order['response']['order_list'][0]['pay_time'] != None:
				pt = order['response']['order_list'][0]['pay_time']
				doc.pay_time = datetime.datetime.fromtimestamp(pt)
						
			doc.note = order['response']['order_list'][0]['note']
			doc.flags.ignore_permissions = True
			doc.save()
			if os == "READY_TO_SHIP":
				make_so(order_sn)
				make_dn(order_sn)
			elif os == "COMPLETED":
				make_pe(order_sn)
				tn = get_tracking_number(doc.shopee_setting,order_sn,doc.package_number)
				if tn['error'] == '':
					frappe.msgprint(tn['response']['tracking_number'])
					frappe.db.sql(""" UPDATE `tabShopee Order` set tracking_no = '{}' where name='{}' """.format(tn['response']['tracking_number'],order_sn))
					frappe.db.commit()
			elif os == "CANCELLED":
				cancel_order(order_sn)
		else:
			doc = frappe.new_doc("Shopee Order")
			doc.order_sn = order_sn
			doc.order_status = order['response']['order_list'][0]['order_status']
			os = order['response']['order_list'][0]['order_status']
			it_id = order['response']['order_list'][0]['item_list'][0]['item_id']
				# model_id = order['response']['order_list'][0]['item_list'][0]['model_id']
			cek_shop_p = frappe.get_value("Item Shopee",{'item_id':it_id}, "shopee_setting")
			doc.shopee_setting = cek_shop_p

			# if os == "READY_TO_SHIP":
			# 	make_so(order_sn)
			# 	make_dn(order_sn)

			doc.customer = order['response']['order_list'][0]['buyer_username']
			ct = order['response']['order_list'][0]['create_time']
			doc.create_time = datetime.datetime.fromtimestamp(ct)
			doc.shopee_order_item=[]
			tmp = []
			tmp_a = []
			for it in order['response']['order_list'][0]['item_list']:
				row = doc.append("shopee_order_item",{})
				frappe.msgprint(str(it['model_id'])+"model_id_123aaaa1")
				if it['model_id'] == 0:
					item_code = frappe.get_value("Item Shopee",{'item_id':it['item_id']}, "item_code")
					row.item_code = item_code
				else:
					item_code_var = frappe.get_value("Table Variation",{'model_id':str(it['model_id'])}, "item_code")
					row.item_code = item_code_var
					
				row.item_id = it['item_id']
				row.item_name = it['item_name']
				row.item_sku = it['item_sku']
				row.model_id = it['model_id']
				row.model_name = it['model_name']
				row.model_sku = it['model_sku']
				row.model_quantity_purchased = it['model_quantity_purchased']
				row.model_discounted_price = it['model_discounted_price']
				row.amount = it['model_quantity_purchased'] * it['model_discounted_price']
				tmp.append(it['weight'] * it['model_quantity_purchased'])
				tmp_a.append(it['model_quantity_purchased'] * it['model_discounted_price'])
			# frappe.msgprint(str(tmp)+"220818EKQDBS20")
			doc.total_orders = sum(tmp_a)
			doc.total_wight = sum(tmp)
			doc.actual_shipping_fee = order['response']['order_list'][0]['actual_shipping_fee']
			doc.estimated_shipping_fee = order['response']['order_list'][0]['estimated_shipping_fee']
			
			if order['response']['order_list'][0]['actual_shipping_fee'] == 0:
				total_sales = sum(tmp_a) + order['response']['order_list'][0]['estimated_shipping_fee']
				doc.total_sales = total_sales
			else:
				total_sales = sum(tmp_a) + order['response']['order_list'][0]['estimated_shipping_fee']
				doc.total_sales = sum(tmp_a) + total_sales
			
			if doc.payment_method == "Indomaret":
				doc.buyer_transaction_fee = 2500
			elif doc.payment_method == "Alfamart":
				doc.buyer_transaction_fee = 2500
			elif doc.payment_method == "COD":
				doc.buyer_transaction_fee = total_sales * 3/100

			doc.total_amount = order['response']['order_list'][0]['total_amount']
			doc.shipping_carrier = order['response']['order_list'][0]['shipping_carrier']
			doc.estimated_shipping_fee = order['response']['order_list'][0]['estimated_shipping_fee']
			doc.package_number = order['response']['order_list'][0]['package_list'][0]['package_number']
			doc.payment_method = order['response']['order_list'][0]['payment_method']
			doc.recipient_name = order['response']['order_list'][0]['recipient_address']['name']
			doc.phone = order['response']['order_list'][0]['recipient_address']['phone']
			doc.district = order['response']['order_list'][0]['recipient_address']['district']
			doc.city = order['response']['order_list'][0]['recipient_address']['city']
			doc.state = order['response']['order_list'][0]['recipient_address']['state']
			doc.zipcode = order['response']['order_list'][0]['recipient_address']['zipcode']
			doc.full_address = order['response']['order_list'][0]['recipient_address']['full_address']
			if order['response']['order_list'][0]['pay_time'] != None:
				pt = order['response']['order_list'][0]['pay_time']
				doc.pay_time = datetime.datetime.fromtimestamp(pt)
				
			doc.note = order['response']['order_list'][0]['note']
			doc.flags.ignore_permissions = True
			doc.save()
			if os == "READY_TO_SHIP":
				make_so(order_sn)
				make_dn(order_sn)

	# doc_t.save(ignore_permissions=True)

@frappe.whitelist(allow_guest=True)
def order_status_push2():
	tmp = json.loads(frappe.request.data)
	doc_t = frappe.new_doc('Log Shopee')
	doc_t.data = """ {} """.format(tmp)
	# reserved_stock_change_push
	if tmp['code'] == 8:
		doc_t.save(ignore_permissions=True)

	# order_trackingno_push
	elif tmp['code'] == 4:
		doc_t.save(ignore_permissions=True)
		doc_os = frappe.get_doc("Shopee Order",tmp['data']['ordersn'])
		doc_os.tracking_no = tmp['data']['tracking_no']
		doc_os.save(ignore_permissions=True)

	# shop_authorization_push
	elif tmp['code'] == 1:
		doc_t.save(ignore_permissions=True)

	# shipping_carrier_update
	elif tmp['code'] == 14:
		doc_t.save(ignore_permissions=True)
	
	# order_status_push
	elif tmp['code'] == 3:
		shop = frappe.get_doc("Shopee Setting",{'shop_id':tmp['shop_id']}).name
		order = get_order_detail(shop,tmp['data']['ordersn'])
		print(order)
		doc_t.order_detail = str(order)
		doc_t.save(ignore_permissions=True)
		order_sn = tmp['data']['ordersn']
		cust = frappe.get_value("Customer",order['response']['order_list'][0]['buyer_username'], "name")
		if cust:
			frappe.msgprint(order['response']['order_list'][0]['buyer_username']+" sudah ada")
		else:
			docc = frappe.new_doc('Customer')
			docc.customer_name = order['response']['order_list'][0]['buyer_username']
			docc.customer_type = 'Individual'

			docc.flags.ignore_permissions=True
			docc.save()
			frappe.msgprint("Make Customer"+order['response']['order_list'][0]['buyer_username'])

		if frappe.db.exists("Shopee Order",str(order_sn)):
			doc = frappe.get_doc("Shopee Order",order_sn)
			doc.order_status = order['response']['order_list'][0]['order_status']
			os = order['response']['order_list'][0]['order_status']
			it_id = order['response']['order_list'][0]['item_list'][0]['item_id']
			# model_id = order['response']['order_list'][0]['item_list'][0]['model_id']
			cek_shop_p = frappe.get_value("Item Shopee",{'item_id':it_id}, "shopee_setting")
			doc.shopee_setting = cek_shop_p

			# if os == "READY_TO_SHIP":
			# 	make_so(order_sn)
			# 	make_dn(order_sn)

			doc.customer = order['response']['order_list'][0]['buyer_username']
			ct = order['response']['order_list'][0]['create_time']
			doc.create_time = datetime.datetime.fromtimestamp(ct)
			doc.shopee_order_item=[]
			tmp = []
			tmp_a = []
			for it in order['response']['order_list'][0]['item_list']:
				row = doc.append("shopee_order_item",{})
				frappe.msgprint(str(it['model_id'])+"model_id_123aaaa2")
				if it['model_id'] == 0:
					item_code = frappe.get_value("Item Shopee",{'item_id':it['item_id']}, "item_code")
					row.item_code = item_code
				else:
					item_code_var = frappe.get_value("Table Variation",{'model_id':str(it['model_id'])}, "item_code")
					row.item_code = item_code_var

				row.item_id = it['item_id']
				row.item_name = it['item_name']
				row.item_sku = it['item_sku']
				row.model_id = it['model_id']
				row.model_name = it['model_name']
				row.model_sku = it['model_sku']
				row.model_quantity_purchased = it['model_quantity_purchased']
				row.model_discounted_price = it['model_discounted_price']
				row.amount = it['model_quantity_purchased'] * it['model_discounted_price']
				tmp.append(it['weight'] * it['model_quantity_purchased'])
				tmp_a.append(it['model_quantity_purchased'] * it['model_discounted_price'])
			# frappe.msgprint(str(tmp)+"220818EKQDBS20")
			doc.total_orders = sum(tmp_a)
			doc.total_wight = sum(tmp)
			doc.actual_shipping_fee = order['response']['order_list'][0]['actual_shipping_fee']
			doc.estimated_shipping_fee = order['response']['order_list'][0]['estimated_shipping_fee']
			
			if order['response']['order_list'][0]['actual_shipping_fee'] == 0:
				total_sales = sum(tmp_a) + order['response']['order_list'][0]['estimated_shipping_fee']
				doc.total_sales = total_sales
			else:
				total_sales = sum(tmp_a) + order['response']['order_list'][0]['estimated_shipping_fee']
				doc.total_sales = sum(tmp_a) + total_sales
			
			if doc.payment_method == "Indomaret":
				doc.buyer_transaction_fee = 2500
			elif doc.payment_method == "Alfamart":
				doc.buyer_transaction_fee = 2500
			elif doc.payment_method == "COD":
				doc.buyer_transaction_fee = total_sales * 3/100

			doc.total_amount = order['response']['order_list'][0]['total_amount']
			doc.shipping_carrier = order['response']['order_list'][0]['shipping_carrier']
			doc.estimated_shipping_fee = order['response']['order_list'][0]['estimated_shipping_fee']
			doc.package_number = order['response']['order_list'][0]['package_list'][0]['package_number']
			doc.payment_method = order['response']['order_list'][0]['payment_method']
			doc.recipient_name = order['response']['order_list'][0]['recipient_address']['name']
			doc.phone = order['response']['order_list'][0]['recipient_address']['phone']
			doc.district = order['response']['order_list'][0]['recipient_address']['district']
			doc.city = order['response']['order_list'][0]['recipient_address']['city']
			doc.state = order['response']['order_list'][0]['recipient_address']['state']
			doc.zipcode = order['response']['order_list'][0]['recipient_address']['zipcode']
			doc.full_address = order['response']['order_list'][0]['recipient_address']['full_address']
			if order['response']['order_list'][0]['pay_time'] != None:
				pt = order['response']['order_list'][0]['pay_time']
				doc.pay_time = datetime.datetime.fromtimestamp(pt)
						
			doc.note = order['response']['order_list'][0]['note']
			doc.flags.ignore_permissions = True
			doc.save()
			if os == "READY_TO_SHIP":
				make_so(order_sn)
				make_dn(order_sn)
			elif os == "COMPLETED":
				make_pe(order_sn)
				tn = get_tracking_number(doc.shopee_setting,order_sn,doc.package_number)
				if tn['error'] == '':
					frappe.msgprint(tn['response']['tracking_number'])
					frappe.db.sql(""" UPDATE `tabShopee Order` set tracking_no = '{}' where name='{}' """.format(tn['response']['tracking_number'],order_sn))
					frappe.db.commit()
			elif os == "CANCELLED":
				cancel_order(order_sn)
		else:
			doc = frappe.new_doc("Shopee Order")
			doc.order_sn = order_sn
			doc.order_status = order['response']['order_list'][0]['order_status']
			os = order['response']['order_list'][0]['order_status']
			it_id = order['response']['order_list'][0]['item_list'][0]['item_id']
				# model_id = order['response']['order_list'][0]['item_list'][0]['model_id']
			cek_shop_p = frappe.get_value("Item Shopee",{'item_id':it_id}, "shopee_setting")
			doc.shopee_setting = cek_shop_p

			# if os == "READY_TO_SHIP":
			# 	make_so(order_sn)
			# 	make_dn(order_sn)

			doc.customer = order['response']['order_list'][0]['buyer_username']
			ct = order['response']['order_list'][0]['create_time']
			doc.create_time = datetime.datetime.fromtimestamp(ct)
			doc.shopee_order_item=[]
			tmp = []
			tmp_a = []
			for it in order['response']['order_list'][0]['item_list']:
				row = doc.append("shopee_order_item",{})
				frappe.msgprint(str(it['model_id'])+"model_id_123aaaa1")
				if it['model_id'] == 0:
					item_code = frappe.get_value("Item Shopee",{'item_id':it['item_id']}, "item_code")
					row.item_code = item_code
				else:
					item_code_var = frappe.get_value("Table Variation",{'model_id':str(it['model_id'])}, "item_code")
					row.item_code = item_code_var
					
				row.item_id = it['item_id']
				row.item_name = it['item_name']
				row.item_sku = it['item_sku']
				row.model_id = it['model_id']
				row.model_name = it['model_name']
				row.model_sku = it['model_sku']
				row.model_quantity_purchased = it['model_quantity_purchased']
				row.model_discounted_price = it['model_discounted_price']
				row.amount = it['model_quantity_purchased'] * it['model_discounted_price']
				tmp.append(it['weight'] * it['model_quantity_purchased'])
				tmp_a.append(it['model_quantity_purchased'] * it['model_discounted_price'])
			# frappe.msgprint(str(tmp)+"220818EKQDBS20")
			doc.total_orders = sum(tmp_a)
			doc.total_wight = sum(tmp)
			doc.actual_shipping_fee = order['response']['order_list'][0]['actual_shipping_fee']
			doc.estimated_shipping_fee = order['response']['order_list'][0]['estimated_shipping_fee']
			
			if order['response']['order_list'][0]['actual_shipping_fee'] == 0:
				total_sales = sum(tmp_a) + order['response']['order_list'][0]['estimated_shipping_fee']
				doc.total_sales = total_sales
			else:
				total_sales = sum(tmp_a) + order['response']['order_list'][0]['estimated_shipping_fee']
				doc.total_sales = sum(tmp_a) + total_sales
			
			if doc.payment_method == "Indomaret":
				doc.buyer_transaction_fee = 2500
			elif doc.payment_method == "Alfamart":
				doc.buyer_transaction_fee = 2500
			elif doc.payment_method == "COD":
				doc.buyer_transaction_fee = total_sales * 3/100

			doc.total_amount = order['response']['order_list'][0]['total_amount']
			doc.shipping_carrier = order['response']['order_list'][0]['shipping_carrier']
			doc.estimated_shipping_fee = order['response']['order_list'][0]['estimated_shipping_fee']
			doc.package_number = order['response']['order_list'][0]['package_list'][0]['package_number']
			doc.payment_method = order['response']['order_list'][0]['payment_method']
			doc.recipient_name = order['response']['order_list'][0]['recipient_address']['name']
			doc.phone = order['response']['order_list'][0]['recipient_address']['phone']
			doc.district = order['response']['order_list'][0]['recipient_address']['district']
			doc.city = order['response']['order_list'][0]['recipient_address']['city']
			doc.state = order['response']['order_list'][0]['recipient_address']['state']
			doc.zipcode = order['response']['order_list'][0]['recipient_address']['zipcode']
			doc.full_address = order['response']['order_list'][0]['recipient_address']['full_address']
			if order['response']['order_list'][0]['pay_time'] != None:
				pt = order['response']['order_list'][0]['pay_time']
				doc.pay_time = datetime.datetime.fromtimestamp(pt)
				
			doc.note = order['response']['order_list'][0]['note']
			doc.flags.ignore_permissions = True
			doc.save()
			if os == "READY_TO_SHIP":
				make_so(order_sn)
				make_dn(order_sn)

@frappe.whitelist()
def make_pe(order_sn):
	frappe.msgprint("hhaha")
	data = frappe.db.sql(""" SELECT * from `tabShopee Order` where name='{}' """.format(order_sn),as_dict=1)
	for i in data:
		detail = get_escrow_detail(i['shopee_setting'],order_sn)
		if detail['error'] == '':
			get_sinv = frappe.db.sql(""" SELECT * from `tabSales Invoice` where marketplace_id ='{}' and docstatus = 1""".format(detail['response']['order_sn']),as_dict=1)
			frappe.msgprint(get_sinv[0]['name']+"huyhuh")
			cek = frappe.get_value("Payment Entry",{'marketplace_id':order_sn}, "name")
			if cek:
				pass
			else:
				pe = frappe.new_doc('Payment Entry')
				pe.marketplace_id = detail['response']['order_sn']
				pe.mode_of_payment = "Cash"
				pe.party_type = 'Customer'
				pe.party = detail['response']['buyer_user_name']
				pe.paid_to = frappe.get_doc("Shopee Setting",i['shopee_setting']).paid_to
				pe.paid_amount = detail['response']['order_income']['buyer_total_amount']
				pe.received_amount = detail['response']['order_income']['buyer_total_amount']
				row = pe.append('references', {})
				row.reference_doctype = 'Sales Invoice'
				row.reference_name = get_sinv[0]['name']
				row.due_date = get_sinv[0]['due_date']
				row.total_amount = get_sinv[0]['grand_total']
				row.outstanding_amount = get_sinv[0]['grand_total']
				row.allocated_amount = get_sinv[0]['grand_total']

				pe.flags.ignore_permissions=True
				pe.save()

		# pe.save(ignore_permissions=True)
		# frappe.msgprint(detail['response']['order_sn'])
		# frappe.msgprint(detail['response']['buyer_user_name'])
		# frappe.msgprint(detail['response']['order_income']['buyer_total_amount'])

@frappe.whitelist()
def cancel_order(order_sn):
	cek_dn = frappe.db.sql(""" SELECT * from `tabDelivery Note` where marketplace_id ='{}' """.format(order_sn),as_dict=1)
	cek_so = frappe.db.sql(""" SELECT * from `tabSales Order` where marketplace_id ='{}' and docstatus = 1  """.format(order_sn),as_dict=1)
	if cek_dn:
		for i in cek_dn:
			if i['docstatus'] == 0:
				doc = frappe.get_doc("Delivery Note",i['name'])
				doc.flags.ignore_permissions = True
				doc.delete()
			elif i['docstatus'] == 1:
				doc = frappe.get_doc("Delivery Note",i['name'])
				doc.flags.ignore_permissions = True
				doc.cancel()
				doc.delete()

	if cek_so:
		for i in cek_so:
			if i['docstatus'] == 1:
				doc = frappe.get_doc("Sales Order",i['name'])
				doc.flags.ignore_permissions = True
				doc.cancel()

@frappe.whitelist()
def cek_fake_stock_shopee():
	data = frappe.db.sql(""" SELECT * from `tabItem Shopee` """,as_dict=1)
	for i in data:
		conter = 0
		if i['type'] == 'Product' and i['item_code']:
			frappe.msgprint(str(i['name']))
			doc = frappe.get_doc("Item Shopee",i['name'])
			tampil = ItemShopee.generate_stock(doc)
			if tampil <= i['min_stock']:
				doc.is_fake = 0
				doc.save()

		if i['type'] == 'Template' and i['item_code']:
			frappe.msgprint(str(i['name'])+"Template")
			doc = frappe.get_doc("Item Shopee",i['name'])
			for i in doc.variation_table:
				
				tampil = ItemShopee.generate_stock_variant(doc, i.item_code,i.bobot)
				if tampil <= i.min_stock:
					# frappe.msgprint(str(tampil)+'conter = 0')
					i.is_fake=0
					i.stock = tampil
					conter = conter + 1
			
			if conter > 0:
				doc.flags.ignore_permissions = True
				doc.save()

@frappe.whitelist()
def calculate_bobot_shopee():
	data = frappe.db.sql(""" SELECT * from `tabItem Shopee` """,as_dict=1)
	cal=0
	for i in data:
		shopeesetting = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE name = '{}' """.format(i['shopee_setting']),as_dict=1)
		for j in shopeesetting:
			saller_test = j['seller_test']
			acces_token = j['access_token']
			partner_id = j['partner_id']
			key = j['key']
			shop_id = j['shop_id']

		if i['type'] == 'Product' and i['item_code']:
			test = get_item_base_info(saller_test,acces_token,partner_id,key,shop_id,i['item_id'])['response']['item_list'][0]['stock_info_v2']['seller_stock'][0]['stock'] if len(get_item_base_info(saller_test,acces_token,partner_id,key,shop_id,i['item_id'])['response']['item_list'][0]['stock_info_v2']) > 1 else 0
			# frappe.msgprint(i[''])
			# frappe.msgprint(str(test)+str(i.Stock)+"xxvvv")
			if test	!= i['stock']:
				doc = frappe.get_doc('Item Shopee',i['name'])
				frappe.msgprint(doc.name+'docname')
				doc.flags.ignore_permissions = True
				doc.save()

		if i['type'] == 'Template' and i['item_code']:
			test = get_model_list(saller_test, acces_token, partner_id,key, shop_id, i['item_id'])
			frappe.msgprint(str(test)+" response get model list")
			dictModelIdStock = {}
			for x in test['response']['model']:
				frappe.msgprint(str(x)+" for get model list xxx")
				# test = get_item_base_info(saller_test,acces_token,partner_id,key,shop_id,self.item_id)['response']['item_list'][0]['stock_info_v2']['seller_stock'][0]['stock'] if len(get_item_base_info(saller_test,acces_token,partner_id,key,shop_id,self.item_id)['response']['item_list'][0]['stock_info_v2']) > 1 else 0			
				dictModelIdStock[x['model_id']] = x['stock_info_v2']['seller_stock'][0]['stock'] if len(x['stock_info_v2']) > 1 else 0
				doc = frappe.get_doc('Item Shopee',i['name'])
				for v in doc.variation_table:
					if int(v.model_id) == x['model_id']:
						frappe.msgprint("zzz123")
						if v.stock == dictModelIdStock[x['model_id']]:
							frappe.msgprint("yyy123")
						else:
							frappe.msgprint("xxx123")
							cal = cal+1
			frappe.msgprint(str(cal)+'cal')
			if cal > 0:
				frappe.msgprint(doc.name+"naming")
				frappe.msgprint("masuk_save")
				doc.save()


	
	# for i in data:
	# 	conter = 0
	# 	if i['type'] == 'Product':
	# 		tampil = get_stock_price(i['name'])
	# 		if tampil <= i['min_stock']:
	# 			doc = frappe.get_doc("Item Shopee",i['name'])
	# 			doc.is_fake = 0
	# 			doc.status_item = "LIMITED"
	# 			doc.flags.ignore_permissions = True
	# 			doc.save()