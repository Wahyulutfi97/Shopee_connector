import hmac
import hashlib
import json
import os
import requests
import time

import frappe


@frappe.whitelist()
def get_escrow_detail(shop_setting,order_sn):
    # shop_setting = "OpenSANDBOX39454f033ed4e413af6a74fa"
    # order_sn = '220831HSSRWTYE'
    data = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` where name ='{}' """.format(shop_setting),as_dict=1)
    for i in data:
        cek = i['seller_test']
        access_token = i['access_token']
        partner_id = i['partner_id']
        partner_key = i['key']
        shop_id = i['shop_id']
        # frappe.msgprint(str(shopee[0].seller_test))
        timest = int(time.time())
        language = "id"    
        if int(cek) > 0:
            host = "https://partner.test-stable.shopeemobile.com"
        else:
            host = "https://partner.shopeemobile.com"
        path = "/api/v2/payment/get_escrow_detail"
        redirect= "https://google.com"
        base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
        sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
        # url = "https://partner.shopeemobile.com/api/v2/logistics/get_shipping_parameter?access_token=access_token&order_sn=201214JASXYXY6&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
        url = str(host+path+"?access_token={}&order_sn={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,order_sn,partner_id,shop_id, sign,timest))
        payload={}
        headers = {

        }
        response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
        ret = json.loads(response.text)
        # frappe.msgprint(str(ret))

        return ret