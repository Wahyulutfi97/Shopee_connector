import hmac
import hashlib
import json
import os
import requests
import time

import frappe

@frappe.whitelist()
def update_brand_using_category_id():
	idCategory = "101961"
	brand = get_brand_list_in_category(0,idCategory)
	count = 1
	while count > 0:
		if brand['error'] == "":
			tmp = []
			for t in brand['response']['brand_list']:
				tmp.append(t)
			for i in tmp:
				if frappe.db.exists("Shopee Brand List",i['brand_id']):
					doc = frappe.get_doc('Shopee Brand List', i['brand_id'])

					temp = json.loads(doc.use_in_category_id)
					temp.append(idCategory)
					doc.use_in_category_id = temp

					doc.save()
				else:
					doc = frappe.new_doc("Shopee Brand List")
					doc.brand_id = i['brand_id']
					doc.original_brand_name = i['original_brand_name']
					doc.display_brand_name = i['display_brand_name']

					temp = []
					temp.append(idCategory)
					doc.use_in_category_id = temp

					doc.flags.ignore_permissions=True
					doc.save()
			if brand['response']['has_next_page'] == True:
				count = 1
				next_offset = brand['response']['next_offset']
				brand = get_brand_list_in_category(next_offset,idCategory)
			else:
				count = 0
				break

@frappe.whitelist()
def get_brand_list_in_category(offset,idCategory):
	shopee = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
	cek = shopee[0].seller_test
	access_token = shopee[0].access_token
	partner_id = shopee[0].partner_id
	partner_key = shopee[0].key
	shop_id = shopee[0].shop_id
	frappe.msgprint(str(shopee[0].seller_test))
	timest = int(time.time())
	language = "id"
	if cek == 1:
		host = "https://partner.test-stable.shopeemobile.com"
	else:
		host = "https://partner.shopeemobile.com"
	path = "/api/v2/product/get_brand_list"
	redirect= "https://google.com"
	base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
	language = "id"
	category_id = idCategory
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
					doc.category_id = "101942"
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

@frappe.whitelist()
def get_brand_list(offset):
	shopee = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
	cek = shopee[0].seller_test
	access_token = shopee[0].access_token
	partner_id = shopee[0].partner_id
	partner_key = shopee[0].key
	shop_id = shopee[0].shop_id
	frappe.msgprint(str(shopee[0].seller_test))
	timest = int(time.time())
	language = "id"
	if cek == 1:
		host = "https://partner.test-stable.shopeemobile.com"
	else:
		host = "https://partner.shopeemobile.com"
	path = "/api/v2/product/get_brand_list"
	redirect= "https://google.com"
	base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
	language = "id"
	category_id = "101955"
	sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	# url = "https://partner.shopeemobile.com/api/v2/product/get_brand_list?access_token=access_token&category_id=12345&language=zh-hans&offset=0&page_size=10&partner_id=partner_id&shop_id=shop_id&sign=sign&status=1&timestamp=timestamp"
	url = str(host+path+"?access_token={}&category_id={}&language={}&offset={}&page_size=100&partner_id={}&shop_id={}&sign={}&status=1&timestamp={}".format(access_token,category_id,language,offset,partner_id,shop_id, sign,timest))
	payload={}
	headers = {

	}
	response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
	ret = json.loads(response.text)
	frappe.msgprint(str(ret))

	return ret
	# print(ret)

@frappe.whitelist()
def get_attributes():
	shopee = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
	cek = shopee[0].seller_test
	access_token = shopee[0].access_token
	partner_id = shopee[0].partner_id
	partner_key = shopee[0].key
	shop_id = shopee[0].shop_id
	frappe.msgprint(str(shopee[0].seller_test))
	timest = int(time.time())
	language = "id"
	category_id = "101944"
	if cek == 1:
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
def get_logistics():
    shopee = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
    cek = shopee[0].seller_test
    access_token = shopee[0].access_token
    partner_id = shopee[0].partner_id
    partner_key = shopee[0].key
    shop_id = shopee[0].shop_id
    frappe.msgprint(str(shopee[0].seller_test))
    timest = int(time.time())
    language = "id"
    if cek == 1:
        host = "https://partner.test-stable.shopeemobile.com"
    else:
        host = "https://partner.shopeemobile.com"
    path = "/api/v2/logistics/get_channel_list"
    redirect= "https://google.com"
    base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
    sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	# url = "https://partner.shopeemobile.com/api/v2/logistics/get_channel_list?access_token=access_token&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
    url = str(host+path+"?access_token={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,partner_id,shop_id, sign,timest))
    payload={}
    headers = {

	}
    response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
    ret = json.loads(response.text)
    frappe.msgprint(str(ret['response']))

@frappe.whitelist()
def mediaspace_upload_img_shopee():
    shopee = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
    cek = shopee[0].seller_test
    partner_id = shopee[0].partner_id
    partner_key = shopee[0].key
    timest = int(time.time())
    if cek == 1:
        host = "https://partner.test-stable.shopeemobile.com"
    else:
        host = "https://partner.shopeemobile.com"
    path = "/api/v2/media_space/upload_image"
    redirect= "https://google.com"
    base_string = "%s%s%s"%(partner_id, path, timest)
    sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	# url = "https://partner.shopeemobile.com/api/v2/media_space/upload_image?partner_id=partner_id&sign=sign&timestamp=timestamp"
    url = str(host+path+"?partner_id={}&sign={}&timestamp={}".format(partner_id, sign,timest))
    payload={}
    files=[
    ('image',('image',open('demo.solubis.id/public/files/test_gambar.jpg','rb'),'application/octet-stream')) # Replace with actual file path
    ]
    headers = {

	}

    frappe.msgprint(str(sign))

    response = requests.request("POST",url,headers=headers, data=payload, files=files, allow_redirects=False)
    frappe.msgprint(str(response.text))

@frappe.whitelist()
def add_item_erp_to_shopee():
	shopee = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
	cek = shopee[0].seller_test
	access_token = shopee[0].access_token
	partner_id = shopee[0].partner_id
	partner_key = shopee[0].key
	shop_id = shopee[0].shop_id
	frappe.msgprint(str(shopee[0].seller_test))
	timest = int(time.time())
	language = "id"
	if cek == 1:
		host = "https://partner.test-stable.shopeemobile.com"
	else:
		host = "https://partner.shopeemobile.com"
	path = "/api/v2/product/add_item"
	redirect= "https://google.com"
	base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
	sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	url = str(host+path+"?access_token={}&language={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,language,partner_id,shop_id, sign,timest))
    # add manual category Hardisk(101961), brand LEXON(3239848), attribute_id External/Internal (100418) => value_id External (2540), image_id_list (5f4b3c60749a560159826f13a339d41c),
	# add manual category RAM(101955), brand ABRA Therapeutics(1014148), attribute_id RAM (100461) => value_id 4GB (5247), image_id_list (5f4b3c60749a560159826f13a339d41c),
	payload=json.dumps({
        "original_price":50000,
        "description":"RAM TESTING LOGISTIK",
		"weight":1.1,
        "item_name":"RAM TESTING",
		"dimension":{
			"package_height":1,
			"package_length":1,
			"package_width":1
		},
        "normal_stock":10,
        "logistic_info":[
            {
                "enabled":True,
                "logistic_id":8001
            },
			{
                "enabled":True,
                "logistic_id":8003
            }
        ],
        "attribute_list":[
            {
                "attribute_id":100461,
                "attribute_value_list":[
                    {
                        "value_id":5247,
						"value_unit":'GB'
                    }
                ]
            }
        ],
        "category_id":101955,
        "image":{
            "image_id_list":[
                "5f4b3c60749a560159826f13a339d41c"
            ]
        },
        "brand":{
            "brand_id":1014148
        }
    })

	resp = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
	ret = json.loads(resp.text)
	frappe.msgprint(str(ret))

@frappe.whitelist()
def update_item_erp_to_shopee():
	shopee = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
	cek = shopee[0].seller_test
	access_token = shopee[0].access_token
	partner_id = shopee[0].partner_id
	partner_key = shopee[0].key
	shop_id = shopee[0].shop_id
	frappe.msgprint(str(shopee[0].seller_test))
	timest = int(time.time())
	language = "id"
	if cek == 1:
		host = "https://partner.test-stable.shopeemobile.com"
	else:
		host = "https://partner.shopeemobile.com"
	path = "/api/v2/product/update_item"
	redirect= "https://google.com"
	base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
	sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	url = str(host+path+"?access_token={}&language={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,language,partner_id,shop_id, sign,timest))
    # add manual category Hardisk(101961), brand LEXON(3239848), attribute_id External/Internal (100418) => value_id External (2540), image_id_list (5f4b3c60749a560159826f13a339d41c),
	# add manual category RAM(101955), brand ABRA Therapeutics(1014148), attribute_id RAM (100461) => value_id 4GB (5247), image_id_list (5f4b3c60749a560159826f13a339d41c),
	payload=json.dumps({
		"item_id": 14291945138,
		"description": "RAM TESTING RAM TESTING RAM TESTING RAM TESTING RAM TESTING RAM TESTING",
		"weight": 1.1,
		"item_name": "asdasd",
		"normal_stock": 10,
		"logistic_info": [
			{
			"enabled": True,
			"logistic_id": 8001
			}
		],
		"item_dangerous": 0,
		"pre_order": {
			"is_pre_order": False
		},
		"condition": "NEW",
		"dimension": {
			"package_height": 1.0,
			"package_length": 1.0,
			"package_width": 1.0
		},
		"attribute_list": [
			{
			"attribute_id": 100461,
			"attribute_value_list": [
				{
				"value_id": 5248,
				"value_unit": "GB"
				}
			]
			},
			{
			"attribute_id": 100439,
			"attribute_value_list": [
				{
				"value_id": 2559
				}
			]
			},
			{
			"attribute_id": 100942,
			"attribute_value_list": [
				{
				"value_id": 0,
				"original_value_name ": "123"
				}
			]
			},
			{
			"attribute_id": 100121,
			"attribute_value_list": [
				{
				"value_id": 776
				}
			]
			},
			{
			"attribute_id": 100370,
			"attribute_value_list": [
				{
				"value_id": 2437
				}
			]
			},
			{
			"attribute_id": 101037,
			"attribute_value_list": [
				{
				"value_id": 5779,
				"value_unit": "GB"
				}
			]
			}
		],
		"category_id": 101955,
		"brand": {
			"brand_id": 1146277
		},
		"image": {
			"image_id_list": [
			"2cacb106535e84b8e96fb6cd54cea6d2",
			"78347fbdd279907cd4f6e7e3b4b96fb5"
			]
		}
		})



	resp = requests.request("POST",url, data=payload, allow_redirects=False)
	ret = json.loads(resp.text)
	frappe.msgprint(str(ret))

@frappe.whitelist()
def add_item_variant_erp_to_shopee():
	shopee = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
	cek = shopee[0].seller_test
	access_token = shopee[0].access_token
	partner_id = shopee[0].partner_id
	partner_key = shopee[0].key
	shop_id = shopee[0].shop_id
	frappe.msgprint(str(shopee[0].seller_test))
	timest = int(time.time())
	if cek == 1:
		host = "https://partner.test-stable.shopeemobile.com"
	else:
		host = "https://partner.shopeemobile.com"
	path = "/api/v2/product/init_tier_variation"
	redirect= "https://google.com"
	base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
	sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	# url = "https://partner.shopeemobile.com/api/v2/product/init_tier_variation?access_token=access_token&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
	url = str(host+path+"?access_token={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,partner_id,shop_id, sign,timest))
	# ID ITEM CONTOH : 18339782788 (TESTING RAM)
	payload=json.dumps({
	"item_id": 18339782788,
	"model": [
		{
		"normal_stock": 892,
		"original_price": 4760,
		"tier_index": [
			0,
			0
		]
		},
		{
		"normal_stock": 12,
		"original_price": 4060,
		"tier_index": [
			1,
			0
		]
		}
	],
	"tier_variation": [
		{
		"name": "Ukuran",
		"option_list": [
			{
			"option": "XL"
			},
			{
			"option": "M"
			}
		]
		},
		{
		"name": "Rasa",
		"option_list": [
			{
			"option": "Manis"
			}
		]
		}
	]
	})

	# payload=json.dumps({
	# "item_id": 18339782788,
	# "model": [
	# 	{
	# 	"normal_stock": 100,
	# 	"original_price": 5000,
	# 	"tier_index": [
	# 		0,
	# 		0
	# 	]
	# 	},
	# 	{
	# 	"normal_stock": 100,
	# 	"original_price": 5000,
	# 	"tier_index": [
	# 		1,
	# 		0
	# 	]
	# 	}
	# ],
	# "tier_variation": [
	# 	{
	# 	"name": "Rasa",
	# 	"option_list": [
	# 		{
	# 		"option": "PEDAS"
	# 		},
	# 		{
	# 		"option": "MANIS"
	# 		}
	# 	]
	# 	},
	# 	{
	# 	"name": "Size",
	# 	"option_list": [
	# 		{
	# 		"option": "Small"
	# 		}
	# 	]
	# 	}
	# ]
	# })

	resp = requests.request("POST",url, data=payload, allow_redirects=False)
	ret = json.loads(resp.text)
	frappe.msgprint(str(ret['response']['model']))

@frappe.whitelist()
def unlist_item_api():
	shopee = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE seller_test = 0 LIMIT 1 """,as_dict=1)
	cek = shopee[0].seller_test
	access_token = shopee[0].access_token
	partner_id = shopee[0].partner_id
	partner_key = shopee[0].key
	shop_id = shopee[0].shop_id
	frappe.msgprint(str(shopee[0].seller_test))
	timest = int(time.time())
	language = "id"
	if cek == 1:
		host = "https://partner.test-stable.shopeemobile.com"
	else:
		host = "https://partner.shopeemobile.com"
	path = "/api/v2/product/unlist_item"
	redirect= "https://google.com"
	base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
	sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	url = str(host+path+"?access_token={}&language={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,language,partner_id,shop_id, sign,timest))   
	payload=json.dumps({
		"item_list": [
			{
				"item_id": 21942714332,
				"unlist": False
			}
		]
	})

	resp = requests.request("POST",url, data=payload, allow_redirects=False)
	ret = json.loads(resp.text)
	frappe.msgprint(str(ret))
