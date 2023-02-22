import hmac
import hashlib
import json
import os
import requests
import time

import frappe

class Attribute():
    @frappe.whitelist()
    def get_attribute_list(cek,access_token,partner_id,partner_key,shop_id,category_id):        
        timest = int(time.time())
        language = "id"    
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
        # frappe.msgprint(str(ret))
        if(len(ret['response'])==0):            
            frappe.throw('Specification not found!')
        else:            
            # frappe.msgprint(str(ret['response']))
            return (ret['response'])

@frappe.whitelist()
def get_attribute_list_js(shopee_setting, category_id):   
    data = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE name = '{}' """.format(shopee_setting),as_dict=1)
    for i in data:
        listAttribute = Attribute.get_attribute_list(i['seller_test'],i['access_token'],i['partner_id'],i['key'],i['shop_id'],category_id)
    
    # frappe.msgprint(str(listAttribute['attribute_list']))    
    return (listAttribute['attribute_list'])