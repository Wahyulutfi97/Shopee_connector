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

@frappe.whitelist()
def get_order_list_ulang(tanggal,shop):
	cursor = ''
	item_sh = get_order_list(tanggal,shop,cursor)
	# frappe.msgprint(str(item_sh)+"get_order_list_ulang")
	count = 1
	while count > 0:
		if item_sh['error'] == "":
			# frappe.msgprint(str(brand['response']))
			tmp = []
			for t in item_sh['response']['order_list']:
				tmp.append(t)
			# frappe.msgprint(str(tmp))
			for tm in tmp:
				order = get_order_detail(shop,tm['order_sn'])
				frappe.msgprint(str(order))
				# frappe.msgprint(order['response']['order_list'][0]['shipping_carrier']+str(order['response']['order_list'][0]['order_sn']))
				order_sn = order['response']['order_list'][0]['order_sn']
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
						frappe.msgprint(str(it['model_id'])+"model_id_123")
						if it['model_id'] == 0:
							item_code = frappe.get_value("Item Shopee",{'item_id':it_id}, "item_code")
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
						# doc.pay_time = order['response']['order_list'][0]['pay_time']
					doc.note = order['response']['order_list'][0]['note']
					doc.flags.ignore_permissions = True
					doc.save()
					if os == "READY_TO_SHIP":
						make_so(order_sn)
						make_dn(order_sn)

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
						frappe.msgprint(str(it['model_id'])+"model_id_123")
						if it['model_id'] == 0:
							item_code = frappe.get_value("Item Shopee",{'item_id':it_id}, "item_code")
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

			if item_sh['response']['more'] == True:
				# frappe.msgprint(str(item_sh['response']['next_offset']))
				count = 1
				next_offset = item_sh['response']['next_cursor']
				item_sh = get_order_list(tanggal,shop,next_offset)
			else:
				count = 0
				break
		else:
			count = 0
			break
			
@frappe.whitelist()
def get_order_list(tanggal,shop,cursor):
	count = 0
	time_from = 0
	time_to = 0
	today = str(tanggal)
	day_sebelumnya = str(add_days(today, -15));
	today_morning = day_sebelumnya + " 23:59:59"
	today_evening = today + " 23:59:59"
	
	time_from = int(time.mktime(datetime.datetime.strptime(str(today_morning), "%Y-%m-%d %H:%M:%S").timetuple()))
	time_to = int(time.mktime(datetime.datetime.strptime(str(today_evening), "%Y-%m-%d %H:%M:%S").timetuple()))
	timest = int(time.time())
	# frappe.msgprint(str(time_from))
	# frappe.msgprint(str(datetime.datetime.fromtimestamp(time_from)))
	
	data = frappe.db.sql(""" SELECT * from `tabShopee Setting` where name='{}' """.format(shop),as_dict=1)
	for i in data:
		cek = i['seller_test']
		partner_id = i['partner_id']
		access_token = i['access_token']
		shop_id = i['shop_id']
		partner_key = i['key']
		language = "id"
		if int(cek) > 0:
			host = "https://partner.test-stable.shopeemobile.com"
		else:
			host = "https://partner.shopeemobile.com"
		path = "/api/v2/order/get_order_list"
		redirect= "https://google.com"
		# cursor = ''
		base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
		sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
		# url = "https://partner.shopeemobile.com/api/v2/order/get_order_list?access_token=access_token&cursor=%22%22&order_status=READY_TO_SHIP&page_size=20&partner_id=partner_id&response_optional_fields=order_status&shop_id=shop_id&sign=sign&time_from=1607235072&time_range_field=create_time&time_to=1608271872&timestamp=timestamp"
		url = str(host+path+"?access_token={}&cursor={}&page_size=100&partner_id={}&shop_id={}&sign={}&time_from={}&time_range_field=create_time&time_to={}&timestamp={}".format(access_token,cursor,partner_id,shop_id,sign,time_from,time_to,timest))
		payload={}
		headers = {

		}
		response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
		ret = json.loads(response.text)
		# frappe.msgprint(str(ret))
		print(ret)
		return ret

@frappe.whitelist()
def get_order_detail(shop,order_sn_list):
	timest = int(time.time())
	data = frappe.db.sql(""" SELECT * from `tabShopee Setting` where name='{}' """.format(shop),as_dict=1)
	for i in data:
		cek = i['seller_test']
		partner_id = i['partner_id']
		access_token = i['access_token']
		shop_id = i['shop_id']
		partner_key = i['key']
		language = "id"
		if int(cek) > 0:
			host = "https://partner.test-stable.shopeemobile.com"
		else:
			host = "https://partner.shopeemobile.com"
		path = "/api/v2/order/get_order_detail"
		redirect= "https://google.com"
		base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
		sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
		response_optional_fields = ["shop_id,shop_name,buyer_user_id,buyer_username,estimated_shipping_fee,recipient_address,actual_shipping_fee,goods_to_declare,note,note_update_time,item_list,pay_time,dropshipper,dropshipper_phone,split_up,buyer_cancel_reason,cancel_by,cancel_reason,actual_shipping_fee_confirmed,buyer_cpf_id,fulfillment_flag,pickup_done_time,package_list,shipping_carrier,payment_method,total_amount,invoice_data,checkout_shipping_carrier,reverse_shipping_fee,order_chargeable_weight_gram"]
		# url = "https://partner.shopeemobile.com/api/v2/order/get_order_detail?access_token=access_token&order_sn_list=%5B201214JASXYXY6%5D&partner_id=partner_id&response_optional_fields=%5Bbuyer_user_id%2Cbuyer_username%2Cestimated_shipping_fee%5D&shop_id=shop_id&sign=sign&timestamp=timestamp"
		# response_optional_fields = [""]
		url = str(host+path+"?access_token={}&order_sn_list={}&partner_id={}&response_optional_fields={}&shop_id={}&sign={}&timestamp={}".format(access_token,order_sn_list,partner_id,response_optional_fields,shop_id,sign,timest))
		# url = str(host+path+"?access_token={}&order_sn_list={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,order_sn_list,partner_id,shop_id,sign,timest))
		payload={}
		headers = {

		}
		response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
		ret = json.loads(response.text)
	
	print(url)
	print(ret)
	# frappe.msgprint(str(ret))
	return ret

@frappe.whitelist()
def make_so(order_sn):
	cek_so = frappe.get_value("Sales Order",{"marketplace_id": order_sn,'docstatus': ['!=',2]}, "name")
	if cek_so:
		frappe.msgprint("SO "+order_sn+" Already Exists !")
	else:
		# get_order = frappe.db.get_list('Shopee Order',filters={'name': order_sn },fields=['*'])
		get_order = frappe.db.sql(""" SELECT * FROM `tabShopee Order` where name = '{}' """.format(order_sn),as_dict=1)
		for i in get_order:
			today = date.today()
			doc = frappe.new_doc('Sales Order')
			doc.customer = i['customer']
			doc.order_type = 'Sales'
			doc.delivery_date = add_days(today, +3)
			doc.marketplace = 'Shopee'
			doc.shop_name = i['shopee_setting']
			doc.marketplace_id = i['name']
			# tgl = str(datasave['data']['shipment_fulfillment']['accept_deadline'])
			# tgl_1 = tgl.replace('T'," ")
			# tgl_2 = tgl_1.replace('Z',"")
			# doc.accept_deadline2 = tgl_2
			doc.selling_price_list = frappe.get_value("Shopee Setting",{"name": i['shopee_setting']}, "price_list")
			get_item = frappe.db.get_list('Shopee Order Item',filters={'parent': i['name'] },fields=['*'])
			# if get_item:
			for j in get_item:
				row = doc.append('items', {})
				# row.item_code = j['item_sku']
				row.item_code = j['item_code']
				row.conversion_factor = 1
				row.qty = j['model_quantity_purchased']
				row.rate = j['model_discounted_price']
				row.price_list_rate = j['model_discounted_price']
				row.warehouse = frappe.get_value("Shopee Setting",{"name": i['shopee_setting']}, "warehouse")
			

			tax_a = frappe.get_value("Shopee Setting",{"name": i['shopee_setting']}, "ongkir_account")
			row_tax = doc.append('taxes',{})
			row_tax.charge_type = "Actual"
			row_tax.account_head = tax_a
			# frappe.to
			if i['actual_shipping_fee'] == 0:
				row_tax.tax_amount = i['estimated_shipping_fee']
			else:
				row_tax.tax_amount = i['actual_shipping_fee']
			
			row_tax.description = tax_a
			doc.flags.ignore_permissions=True
			doc.save()
			doc.submit()
			frappe.msgprint("Make So "+ i['name'])

@frappe.whitelist()
def make_dn(order_sn):
	cek_dn = frappe.get_value("Delivery Note",{"marketplace_id": order_sn,'docstatus': ['!=',2]}, "name")
	cek_so = frappe.get_value("Sales Order",{"marketplace_id": order_sn,'docstatus': ['=',1]}, "name")
	if cek_dn:
		frappe.msgprint("DN "+order_sn+" Already Exists !")
	else:
		# get_order = frappe.db.get_list('Shopee Order',filters={'name': order_sn },fields=['*'])
		get_order = frappe.db.sql(""" SELECT * FROM `tabShopee Order` where name = '{}' """.format(order_sn),as_dict=1)
		for i in get_order:
			today = date.today()
			doc = frappe.new_doc('Delivery Note')
			doc.customer = i['customer']
			doc.marketplace = 'Shopee'
			doc.shop_name = i['shopee_setting']
			doc.marketplace_id = i['name']
			doc.tracking_no = i['package_number']
			doc.selling_price_list = frappe.get_value("Shopee Setting",{"name": i['shopee_setting']}, "price_list")
			get_item = frappe.db.get_list('Shopee Order Item',filters={'parent': i['name'] },fields=['*'])
			# if get_item:
			for j in get_item:
				row = doc.append('items', {})
				# row.item_code = j['item_sku']
				row.item_code = j['item_code']
				row.conversion_factor = 1
				row.qty = j['model_quantity_purchased']
				row.rate = j['model_discounted_price']
				row.against_sales_order = cek_so
				row.price_list_rate = j['model_discounted_price']
				row.warehouse = frappe.get_value("Shopee Setting",{"name": i['shopee_setting']}, "warehouse")
			

			tax_a = frappe.get_value("Shopee Setting",{"name": i['shopee_setting']}, "ongkir_account")
			row_tax = doc.append('taxes',{})
			row_tax.charge_type = "Actual"
			row_tax.account_head = tax_a
			# frappe.to
			if i['actual_shipping_fee'] == 0:
				row_tax.tax_amount = i['estimated_shipping_fee']
			else:
				row_tax.tax_amount = i['actual_shipping_fee']
			
			row_tax.description = tax_a
			doc.flags.ignore_permissions=True
			doc.save()
			# doc.submit()
			frappe.msgprint("Make DN "+ i['name'])

@frappe.whitelist()
def make_sinv_dn(self,method):
	cek_sinv = frappe.get_value("Sales Invoice",{"marketplace_id": self.marketplace_id,'docstatus': ['!=',2]}, "name")
	cek_dn = frappe.get_value("Delivery Note",{"marketplace_id": self.marketplace_id,'docstatus': ['=',1]}, "name")
	cek_so = frappe.get_value("Sales Order",{"marketplace_id": self.marketplace_id,'docstatus': ['=',1]}, "name")
	if cek_sinv:
		frappe.msgprint("SINV "+order_sn+" Already Exists !")
	else:
		get_order = frappe.db.get_list('Shopee Order',filters={'name': self.marketplace_id },fields=['*'])
		if get_order:
			for i in get_order:
				today = date.today()
				doc = frappe.new_doc('Sales Invoice')
				doc.customer = i['customer']
				doc.marketplace = 'Shopee'
				doc.shop_name = i['shopee_setting']
				doc.marketplace_id = i['name']
				doc.kurir = i['shipping_carrier']
				doc.selling_price_list = frappe.get_value("Shopee Setting",{"name": i['shopee_setting']}, "price_list")
				get_item = frappe.db.get_list('Shopee Order Item',filters={'parent': i['name'] },fields=['*'])
				# if get_item:
				for j in get_item:
					row = doc.append('items', {})
					# row.item_code = j['item_sku']
					row.item_code = j['item_code']
					row.conversion_factor = 1
					row.qty = j['model_quantity_purchased']
					row.rate = j['model_discounted_price']
					row.sales_order = cek_so
					row.delivery_note = self.name
					row.price_list_rate = j['model_discounted_price']
					row.warehouse = frappe.get_value("Shopee Setting",{"name": i['shopee_setting']}, "warehouse")
				

				tax_a = frappe.get_value("Shopee Setting",{"name": i['shopee_setting']}, "ongkir_account")
				row_tax = doc.append('taxes',{})
				row_tax.charge_type = "Actual"
				row_tax.account_head = tax_a
				# frappe.to
				if i['actual_shipping_fee'] == 0:
					row_tax.tax_amount = i['estimated_shipping_fee']
				else:
					row_tax.tax_amount = i['actual_shipping_fee']
				
				row_tax.description = tax_a
				doc.flags.ignore_permissions=True
				doc.save()
				# doc.submit()
				frappe.msgprint("Make SINV "+ i['name'])
