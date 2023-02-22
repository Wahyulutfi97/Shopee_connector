import hmac
import hashlib
import json
import os
import requests
import time

import frappe

class Auth():
	@frappe.whitelist()
	def test_auth(cek,partner_id,partner_key):
		timest = int(time.time())
		if int(cek) > 0:
			host = "https://partner.test-stable.shopeemobile.com"
		else:
			host = "https://partner.shopeemobile.com"
		path = "/api/v2/shop/auth_partner"
		# https://partner.test-stable.shopeemobile.com
		
		partner_id = partner_id
		redirect= "https://google.com"
		partner_key = partner_key
		base_string = "%s%s%s"%(partner_id, path, timest)
		sign = hmac.new( partner_key.encode(), base_string.encode() , hashlib.sha256).hexdigest()
		url = str(host+path+"?partner_id={}&timestamp={}&sign={}&redirect={}".format(partner_id, timest, sign, redirect))
		frappe.msgprint(url)
		print(url)
		return url
	
	@frappe.whitelist()
	def gen_token_rt(cek,shop_id,partner_id,partner_key,refresh_code):
		timest = int(time.time())
		if int(cek) > 0:
			host = "https://partner.test-stable.shopeemobile.com"
		else:
			host = "https://partner.shopeemobile.com"
		path = "/api/v2/auth/access_token/get"
		redirect= "https://google.com"
		base_string = "%s%s%s"%(partner_id, path, timest)
		sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
		url = str(host+path+"?partner_id={}&timestamp={}&sign={}".format(partner_id, timest, sign))
		body = {"shop_id":int(shop_id), "refresh_token": refresh_code, "partner_id":int(partner_id)}
		headers = { "Content-Type": "application/json"}
		resp = requests.post(url, json=body, headers=headers)
		ret = json.loads(resp.text)
		# frappe.msgprint(str(ret))
		return ret

	@frappe.whitelist()
	def gen_token_code(cek,partner_id,partner_key,shop_code):
		if int(cek) > 0:
			host = "https://partner.test-stable.shopeemobile.com"
		else:
			host = "https://partner.shopeemobile.com"

		timest = int(time.time())
		path = "/api/v2/public/get_token_by_resend_code"
		# base_string = partner_id+path+str(timest)+partner_key
		base_string = "%s%s%s"%(partner_id,path,timest)
		hash_token = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
		url = str(host+path+"?partner_id={}&sign={}&timestamp={}".format(partner_id,hash_token,timest))
		frappe.msgprint(url)
		payload=json.dumps({
		  "resend_code": shop_code
		})
		headers = {
		  'Content-Type': 'application/json'
		}
		#resp = requests.post(url, headers=headers,json=body,allow_redirects=False)
		resp = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
		ret = json.loads(resp.text)
		frappe.msgprint(str(ret))
		
	@frappe.whitelist()
	def test_toko(cek,shop_id,partner_id,partner_key,access_token):
		timest = int(time.time())
		if int(cek) > 0:
			host = "https://partner.test-stable.shopeemobile.com"
		else:
			host = "https://partner.shopeemobile.com"
		path = "/api/v2/shop/get_shop_info"
		redirect= "https://google.com"
		base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
		sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
		url = str(host+path+"?access_token={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,partner_id,shop_id, sign,timest))
		payload={}
		headers = {

		}
		response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
		ret = json.loads(response.text)
		# frappe.msgprint(str(ret['shop_name']))
		print(ret)
	
	@frappe.whitelist()
	def test_token(cek,shop_id,partner_id,partner_key,code):
		if int(cek) > 0:
			host = "https://partner.test-stable.shopeemobile.com"
		else:
			host = "https://partner.shopeemobile.com"
		timest = int(time.time())
		path = "/api/v2/auth/token/get"
		redirect= "https://google.com"
		base_string = "%s%s%s"%(partner_id, path, timest)
		sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
		url = str(host+path+"?partner_id={}&timestamp={}&sign={}".format(partner_id, timest, sign))
		body = {"code":code, "shop_id":int(shop_id), "partner_id": int(partner_id)}
		headers = { "Content-Type": "application/json"}
		resp = requests.post(url, json=body, headers=headers)
		ret = json.loads(resp.text)
		frappe.msgprint(url)
		frappe.msgprint(str(ret)+"123")
		print(ret)
		return ret

@frappe.whitelist()
def gen_token_hourly():
	data = frappe.db.sql(""" SELECT * from `tabShopee Setting` where enable_sync = 1 """,as_dict=1)
	for i in data:
		test = gen_token_rt_auto(i['seller_test'],i['shop_id'],i['partner_id'],i['key'],i['refresh_token'])
		doc = frappe.get_doc('Shopee Setting',i['name'])
		if test['message'] == "Invalid refresh_token.":
			test2 = gen_token_rt_auto(i['seller_test'],i['shop_id'],i['partner_id'],i['key'],i['new_refresh_token'])
			doc.access_token = test2['access_token']
			doc.new_refresh_token = test2['refresh_token']
			doc.flags.ignore_permissions=True
			doc.save()
		else:
			doc.access_token = test['access_token']
			doc.flags.ignore_permissions=True
			doc.save()


@frappe.whitelist()
def gen_token_rt_auto(cek,shop_id,partner_id,partner_key,refresh_code):
		timest = int(time.time())
		if int(cek) > 0:
			host = "https://partner.test-stable.shopeemobile.com"
		else:
			host = "https://partner.shopeemobile.com"
		path = "/api/v2/auth/access_token/get"
		redirect= "https://google.com"
		base_string = "%s%s%s"%(partner_id, path, timest)
		sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
		url = str(host+path+"?partner_id={}&timestamp={}&sign={}".format(partner_id, timest, sign))
		body = {"shop_id":int(shop_id), "refresh_token": refresh_code, "partner_id":int(partner_id)}
		headers = { "Content-Type": "application/json"}
		resp = requests.post(url, json=body, headers=headers)
		ret = json.loads(resp.text)
		frappe.msgprint(str(ret))
		return ret