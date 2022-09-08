import hmac
import hashlib
import json
import os
import requests
import time

import frappe

class Product():
	@frappe.whitelist()
	def get_category(cek,access_token,partner_id,partner_key,shop_id):
		timest = int(time.time())
		language = "id"
		if int(cek) > 0:
			host = "https://partner.test-stable.shopeemobile.com"
		else:
			host = "https://partner.shopeemobile.com"
		path = "/api/v2/product/get_category"
		redirect= "https://google.com"
		base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
		sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
		url = "https://partner.shopeemobile.com/api/v2/product/get_category?access_token=access_token&language=zh-hans&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
		url = str(host+path+"?access_token={}&language={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,language,partner_id,shop_id, sign,timest))
		payload={}
		headers = {

		}
		response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
		ret = json.loads(response.text)
		frappe.msgprint(str(ret))
		print(ret)


@frappe.whitelist()
def get_attributes():
	shopee = frappe.db.sql(""" SELECT * FROM `tabShoppe Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
	cek = shopee[0].seller_test
	access_token = shopee[0].access_token
	partner_id = shopee[0].partner_id
	partner_key = shopee[0].key
	shop_id = shopee[0].shop_id
	frappe.msgprint(str(shopee[0].seller_test))
	timest = int(time.time())
	language = "id"
	category_id = "101923"
	if int(cek) > 0:
		host = "https://partner.test-stable.shopeemobile.com"
	else:
		host = "https://partner.shopeemobile.com"
	path = "/api/v2/product/get_attributes"
	redirect= "https://google.com"
	base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
	sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	# url = "https://partner.shopeemobile.com/api/v2/product/get_attributes?access_token=access_token&category_id=0&language=zh-hans&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
	url = str(host+path+"?access_token={}&category_id={}&language={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,category_id,language,partner_id,shop_id, sign,timest))
	payload={}
	headers = {

	}
	response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
	ret = json.loads(response.text)

	frappe.msgprint(str(ret['response']))

@frappe.whitelist()
def get_category_all():
	shopee = frappe.db.sql(""" SELECT * FROM `tabShoppe Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
	cek = shopee[0].seller_test
	access_token = shopee[0].access_token
	partner_id = shopee[0].partner_id
	partner_key = shopee[0].key
	shop_id = shopee[0].shop_id
	frappe.msgprint(str(shopee[0].seller_test))
	timest = int(time.time())
	language = "id"
	if int(cek) > 0:
		host = "https://partner.test-stable.shopeemobile.com"
	else:
		host = "https://partner.shopeemobile.com"
	path = "/api/v2/product/get_category"
	redirect= "https://google.com"
	base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
	sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	url = str(host+path+"?access_token={}&language={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,language,partner_id,shop_id, sign,timest))
	payload={}
	headers = {

	}
	response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
	ret = json.loads(response.text)
	cp = frappe.db.sql(""" SELECT * FROM `tabChild 3` where has_children = 1 """,as_dict=1)
	# frappe.msgprint(str(ret))
	for i in ret['response']['category_list']:
		for j in cp:
		# frappe.msgprint(str(j['name']))
			if i['parent_category_id'] == int(j['name']):
				frappe.msgprint(str(i))
				# doc_c = frappe.get_doc('Child 4',i['category_id'])
				# if doc_c:
				# 	frappe.msgprint(doc_c.name)
				# else:
				doc = frappe.new_doc("Child 4")
				doc.category_id = i['category_id']
				doc.parent_category_id = i['parent_category_id']
				doc.original_category_name = i['original_category_name']
				doc.display_category_name = i['display_category_name']
				doc.has_children = i['has_children']
				doc.flags.ignore_permission=True
				doc.save()
	print(ret)


@frappe.whitelist()
def get_item_list_ulang(name,cek,access_token,partner_id,partner_key,shop_id):
	item_sh = get_item_list(cek,access_token,partner_id,partner_key,shop_id,0)
	# frappe.msgprint(str(item_sh))
	count = 1
	while count > 0:
		if item_sh['error'] == "":
			# frappe.msgprint(str(brand['response']))
			tmp = []
			for t in item_sh['response']['item']:
				tmp.append(t)
			frappe.msgprint(str(tmp)+"tmp")
			for i in tmp:
				# frappe.msgprint(str(i['item_id']))
				get_item_to_erp(name,cek,access_token,partner_id,partner_key,shop_id,i['item_id'])
			if item_sh['response']['has_next_page'] == True:
				# frappe.msgprint(str(item_sh['response']['next_offset']))
				count = 1
				next_offset = item_sh['response']['next_offset']
				item_sh = get_item_list(cek,access_token,partner_id,partner_key,shop_id,next_offset)
			else:
				count = 0
				break
		else:
			count = 0
			break

@frappe.whitelist()
def get_item_list(cek,access_token,partner_id,partner_key,shop_id,offset):
	# shopee = frappe.db.sql(""" SELECT * FROM `tabShoppe Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
	# cek = shopee[0].seller_test
	# access_token = shopee[0].access_token
	# partner_id = shopee[0].partner_id
	# partner_key = shopee[0].key
	# shop_id = shopee[0].shop_id
	# frappe.msgprint(str(shopee[0].seller_test))
	timest = int(time.time())
	language = "id"
	# frappe.msgprint(str(cek))
	
	if int(cek) > 0:
		# frappe.msgprint('asd')
		host = "https://partner.test-stable.shopeemobile.com"
	else:
		# frappe.msgprint('efg')
		host = "https://partner.shopeemobile.com"

	path = "/api/v2/product/get_item_list"
	redirect= "https://google.com"
	base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
	sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	# url = "https://partner.shopeemobile.com/api/v2/product/get_item_list?access_token=access_token&item_status=NORMAL&offset=0&page_size=10&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp&update_time_from=1611311600&update_time_to=1611311631"
	url = str(host+path+"?access_token={}&item_status=NORMAL&offset={}&page_size=100&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,offset,partner_id,shop_id,sign,timest))
	payload={}
	headers = {

	}
	response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
	ret = json.loads(response.text)
	# frappe.msgprint(url)
	frappe.msgprint(str(ret)+"ret_")
	return ret

@frappe.whitelist()
def get_brand_list_ulang():
	brand = get_brand_list(0)
	frappe.msgprint(str(brand))
	count = 1
	while count > 0:
		if brand['error'] == "":
			# frappe.msgprint(str(brand['response']))
			tmp = []
			for t in brand['response']['brand_list']:
				tmp.append(t)
			frappe.msgprint(str(tmp)+"tmp")
			for i in tmp:
				# frappe.msgprint(i['original_brand_name'])
				if frappe.db.exists("Shopee Brand",i['brand_id']):
					pass
				else:
					doc = frappe.new_doc("Shopee Brand")
					doc.brand_id = i['brand_id']
					doc.original_brand_name = i['original_brand_name']
					doc.display_brand_name = i['display_brand_name']
					doc.document = "Child 2"
					doc.category_id = "101961"
					doc.flags.ignore_permissions=True
					doc.save()
			if brand['response']['has_next_page'] == True:
				frappe.msgprint(str(brand['response']['next_offset']))
				count = 1
				next_offset = brand['response']['next_offset']
				brand = get_brand_list(next_offset)
			else:
				count = 0
				break
		else:
			count = 0
			break
			
@frappe.whitelist()
def get_brand_list(offset):
	shopee = frappe.db.sql(""" SELECT * FROM `tabShoppe Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
	cek = shopee[0].seller_test
	access_token = shopee[0].access_token
	partner_id = shopee[0].partner_id
	partner_key = shopee[0].key
	shop_id = shopee[0].shop_id
	frappe.msgprint(str(shopee[0].seller_test))
	timest = int(time.time())
	language = "id"
	if int(cek) > 0:
		host = "https://partner.test-stable.shopeemobile.com"
	else:
		host = "https://partner.shopeemobile.com"
	path = "/api/v2/product/get_brand_list"
	redirect= "https://google.com"
	base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
	language = "id"
	category_id = "101961"
	sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	# url = "https://partner.shopeemobile.com/api/v2/product/get_brand_list?access_token=access_token&category_id=12345&language=zh-hans&offset=0&page_size=10&partner_id=partner_id&shop_id=shop_id&sign=sign&status=1&timestamp=timestamp"
	url = str(host+path+"?access_token={}&category_id={}&language={}&offset={}&page_size=100&partner_id={}&shop_id={}&sign={}&status=1&timestamp={}".format(access_token,category_id,language,offset,partner_id,shop_id, sign,timest))
	payload={}
	headers = {

	}
	response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
	ret = json.loads(response.text)
	
	return ret
	# print(ret)

@frappe.whitelist()
def get_model_list(cek,access_token,partner_id,partner_key,shop_id,item_id_list):
	# shopee = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
	# cek = shopee[0].seller_test
	# access_token = shopee[0].access_token
	# partner_id = shopee[0].partner_id
	# partner_key = shopee[0].key
	# shop_id = shopee[0].shop_id
	# frappe.msgprint(str(shopee[0].seller_test))
	timest = int(time.time())
	language = "id"
	if int(cek) > 0:
		host = "https://partner.test-stable.shopeemobile.com"
	else:
		host = "https://partner.shopeemobile.com"
	path = "/api/v2/product/get_model_list"
	redirect= "https://google.com"
	# item_id_list = 10243842381
	# 13836603177
	base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
	sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	# url = "https://partner.shopeemobile.com/api/v2/product/get_model_list?access_token=access_token&item_id=178312&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
	url = str(host+path+"?access_token={}&item_id={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,item_id_list,partner_id,shop_id,sign,timest))
	
	# url = str(host+path+"?access_token={}&item_id_list={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,item_id_list,partner_id,shop_id,sign,timest))
	
	# frappe.msgprint(url)
	payload={}
	headers = {

	}
	response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
	ret = json.loads(response.text)
	
	# frappe.msgprint(str(ret))
	return ret

@frappe.whitelist()
def get_item_base_info(cek,access_token,partner_id,partner_key,shop_id,item_id_list):
	# shopee = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
	# cek = shopee[0].seller_test
	# access_token = shopee[0].access_token
	# partner_id = shopee[0].partner_id
	# partner_key = shopee[0].key
	# shop_id = shopee[0].shop_id
	# frappe.msgprint(str(shopee[0].seller_test))
	timest = int(time.time())
	language = "id"
	if int(cek) > 0:
		host = "https://partner.test-stable.shopeemobile.com"
	else:
		host = "https://partner.shopeemobile.com"
	path = "/api/v2/product/get_item_base_info"
	redirect= "https://google.com"
	# item_id_list = 10243842381
	# 13836603177
	base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
	sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	# url = "https://partner.shopeemobile.com/api/v2/product/get_item_base_info?access_token=access_token&item_id_list=34001,34002&need_complaint_policy=true&need_tax_info=true&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
	url = str(host+path+"?access_token={}&item_id_list={}&need_complaint_policy=true&need_tax_info=true&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,item_id_list,partner_id,shop_id,sign,timest))
	# url = str(host+path+"?access_token={}&item_id_list={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,item_id_list,partner_id,shop_id,sign,timest))
	
	# frappe.msgprint(url)
	payload={}
	headers = {

	}
	response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
	ret = json.loads(response.text)
	
	# frappe.msgprint(str(ret['response']))
	return ret

@frappe.whitelist()
def get_item_to_erp(name,cek,access_token,partner_id,partner_key,shop_id,item_id_list):
	data = get_item_base_info(cek,access_token,partner_id,partner_key,shop_id,item_id_list)
	frappe.msgprint(str(data))
	for i in data['response']['item_list']:
		if frappe.db.exists("Item Shopee",{'item_id':str(i['item_id'])}):
			# pass
			frappe.msgprint(str(len(i['brand'])))
		else:
			doc = frappe.new_doc('Item Shopee')
			doc.shopee_setting = name
			doc.item_id = i['item_id']
			doc.item_name = i['item_name']
			doc.item_sku = i['item_sku']
			if len(i['brand'])>0:
				doc.id_brand = i['brand']['brand_id']
				doc.brand = frappe.get_doc('Shopee Brand',i['brand']['brand_id']).display_brand_name
			if i['pre_order']['is_pre_order'] == True:
				doc.pre_order = 1
				doc.days = i['pre_order']['days_to_ship']
			doc.condition = i['condition']
			if i['item_dangerous'] == 1:
				doc.item_dangerous = 1
			# frappe.msgprint("Child_4213123")
			if frappe.db.exists("Child 4",i['category_id']):
				# frappe.msgprint("Child_4")
				child_4 = frappe.get_doc('Child 4',i['category_id'])
				if child_4:
					doc.child_4 = child_4.name
					
					doc.child_3 = frappe.get_doc('Child 3',{'name':child_4.parent_category_id}).name
					child_3 = frappe.get_doc('Child 3',{'name':child_4.parent_category_id}).parent_category_id
					
					doc.child_2 = frappe.get_doc('Child 2',{'name':child_3}).name
					child_2 = frappe.get_doc('Child 2',{'name':child_3}).parent_category_id
					
					doc.child_1 = frappe.get_doc('Child 1',{'name':child_2}).name
					child_1 = frappe.get_doc('Child 1',{'name':child_2}).parent_category_id
					
					doc.category_parent = frappe.get_doc('Category Parent',{'name':child_1}).name
				
			if frappe.db.exists("Child 3",i['category_id']):
				child_3 = frappe.get_doc('Child 3',i['category_id'])
				if child_3:
					# frappe.msgprint('child_3')
					doc.child_3 = child_3.name

					doc.child_2 = frappe.get_doc('Child 2',{'name':child_3.parent_category_id}).name
					child_2 = frappe.get_doc('Child 2',{'name':child_3.parent_category_id}).parent_category_id
					
					doc.child_1 = frappe.get_doc('Child 1',{'name':child_2}).name
					child_1 = frappe.get_doc('Child 1',{'name':child_2}).parent_category_id
					
					doc.category_parent = frappe.get_doc('Category Parent',{'name':child_1}).name

			if frappe.db.exists("Child 2",i['category_id']):
				frappe.msgprint('child_2')
				child_2 = frappe.get_doc('Child 2',i['category_id'])
				if child_2:
					doc.child_2 = child_2.name

					doc.child_1 = frappe.get_doc('Child 1',{'name':child_2.parent_category_id}).name
					child_1 = frappe.get_doc('Child 1',{'name':child_2.parent_category_id}).parent_category_id
					
					doc.category_parent = frappe.get_doc('Category Parent',{'name':child_1}).name

			if frappe.db.exists("Child 1",i['category_id']):
				frappe.msgprint('child_1')
				child_1 = frappe.get_doc('Child 1',i['category_id'])
				if child_1:
					doc.child_1 = child_1.name
					
					doc.category_parent = frappe.get_doc('Category Parent',{'name':child_1.parent_category_id}).name


			for r in i['logistic_info']:
				row = doc.append('losgistic_table', {})
				row.logistic_id= r['logistic_id']
				row.logistic_name= r['logistic_name']
				if r['enabled'] == True:
					row.enabled = 1
				else:
					row.enabled = 0

			if i['has_model'] == True:
				doc.type = "Template"
				var = get_model_list(cek,access_token,partner_id,partner_key,shop_id,i['item_id'])
				# frappe.msgprint(str(var)+'var')
				# for v in var['response']:
				if len(var['response']['tier_variation']) > 1:
					doc.name_variation_1 = var['response']['tier_variation'][0]['name']
					for tv1 in var['response']['tier_variation'][0]['option_list']:
						row = doc.append('variation_1', {})
						row.option= tv1['option']

					doc.name_variation_2 = var['response']['tier_variation'][1]['name']
					for tv2 in var['response']['tier_variation'][1]['option_list']:
						row = doc.append('variation_2', {})
						row.option= tv2['option']
				else:
					doc.name_variation_1 = var['response']['tier_variation'][0]['name']
					for tv1 in var['response']['tier_variation'][0]['option_list']:
						row = doc.append('variation_1', {})
						row.option= tv1['option']

				for m in var['response']['model']:
					if len(var['response']['tier_variation']) > 1:
						row = doc.append('variation_table', {})
						row.model_id = m['model_id']
						row.variation_1 = doc.variation_1[m['tier_index'][0]].option
						row.variation_2 = doc.variation_2[m['tier_index'][1]].option
						# frappe.msgprint(doc.variation_2[m['tier_index'][1]].option+'option')
						row.stock = m['stock_info_v2']['summary_info']['total_available_stock']
						row.model_sku = m['model_sku']
					else:
						row = doc.append('variation_table', {})
						row.model_id = m['model_id']
						row.variation_1 = doc.variation_1[m['tier_index'][0]].option
						row.stock = m['stock_info_v2']['summary_info']['total_available_stock']
						row.model_sku = m['model_sku']
			else:
				doc.stock = i['stock_info'][0]['current_stock']
				doc.type = 'Product'


			doc.flags.ignore_permissions = True
			doc.save()
			frappe.msgprint("Insert Succsess !")

@frappe.whitelist()
def pacth_child1():
	data = frappe.db.get_list("Child 1",fields=['*'])
	for i in data:
		doc = frappe.get_doc('Child 1',i.name)
		frappe.msgprint(doc.name)
		doc.parent_category_name = frappe.get_doc('Category Parent',i['parent_category_id']).display_category_name
		doc.flags.ignore_permissions=True
		doc.save()
		# frappe.msgprint(frappe.get_doc('Category Parent',i['parent_category_id']).display_category_name)
	frappe.msgprint(str(data))

@frappe.whitelist()
def add_item_erp_to_shopee():
	shopee = frappe.db.sql(""" SELECT * FROM `tabShoppe Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
	cek = shopee[0].seller_test
	access_token = shopee[0].access_token
	partner_id = shopee[0].partner_id
	partner_key = shopee[0].key
	shop_id = shopee[0].shop_id
	frappe.msgprint(str(shopee[0].seller_test))
	timest = int(time.time())
	language = "id"
	if int(cek) > 0:
		host = "https://partner.test-stable.shopeemobile.com"
	else:
		host = "https://partner.shopeemobile.com"
	path = "/api/v2/product/add_item"
	redirect= "https://google.com"
	base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
	sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	url = str(host+path+"?access_token={}&language={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,language,partner_id,shop_id, sign,timest))
	payload=json.dumps({
		  {
			"description":"fewajidfosa jioajfiodsa fewajfioewa jicoxjsi fjdiao fjeiwao fdsjiao fejwiao jfdsioafjeiowa jfidsax",
			"item_name":"Hello WXwhGUCI574UsyBHu5J2indlBT6s08av",
			"category_id":14695,
			"brand":{
				"brand_id":123,
				"original_brand_name":"nike"
			},
			"logistic_info":[
				{
					"sizeid":0,
					"shipping_fee":23.12,
					"enabled":True,
					"is_free":False,
					"logistic_id":80101
				},
				{
					"shipping_fee":20000,
					"enabled":True,
					"is_free":False,
					"logistic_id":80106
				},
				{
					"is_free":False,
					"enabled":False,
					"logistic_id":86668
				},
				{
					"enabled":True,
					"price":12000,
					"is_free":True,
					"logistic_id":88001
				},
				{
					"enabled":False,
					"price":2,
					"is_free":False,
					"logistic_id":88014
				}
			],
			"weight":1.1,
			"item_status":"UNLIST",
			"image":{
				"image_id_list":[
					"a17bb867ecfe900e92e460c57b892590",
					"30aa47695d1afb99e296956699f67be6",
					"2ffd521a59da66f9489fa41b5824bb62"
				]
			},
			"dimension":{
				"package_height":11,
				"package_length":11,
				"package_width":11
			},
			"attribute_list":[
				{
					"attribute_id":4811,
					"attribute_value_list":[
						{
							"value_id":0,
							"original_value_name":"",
							"value_unit":""
						}
					]
				}
			],
			"original_price":123.3,
			"seller_stock": [
				{
					"stock": 0
				}
			],
			"tax_info":{
				"ncm":"123",
				"same_state_cfop":"123",
				"diff_state_cfop":"123",
				"csosn":"123",
				"origin":"1",
				"cest":"12345",
				"measure_unit":"1"
			},
			"complaint_policy":{
				"warranty_time":"ONE_YEAR",
				"exclude_entrepreneur_warranty":"123",
				"diff_state_cfop":True,
				"complaint_address_id":123456,
				"additional_information":""
			},
			"description_type":"extended",
			"description_info":{
				"extended_description":{
					"field_list":[
						{
							"field_type":"text",
							"text":"text description 1"
						},
						{
							"field_type":"image",
							"image_info":{
								"image_id":"1e076dff0699d8e778c06dd6c02df1fe"
							}
						},
						{
							"field_type":"image",
							"image_info":{
								"image_id":"c07ac95ba7bb624d731e37fe2f0349de"
							}
						},
						{
							"field_type":"text",
							"text":"text description 1"
						}
					]
				}
			}
		}
		})
	headers = {
		'Content-Type': 'application/json'
	}	

	resp = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
	ret = json.loads(resp.text)
	frappe.msprint(str(ret))