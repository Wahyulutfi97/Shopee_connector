import hmac
import hashlib
import json
import os
import requests
import time

import frappe


class Logistic():
    @frappe.whitelist()
    def get_channel_list(cek,access_token,partner_id,partner_key,shop_id):
        # frappe.msgprint(str(shopee[0].seller_test))
        timest = int(time.time())
        language = "id"    
        if int(cek) > 0:
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
        frappe.msgprint(str(ret))
        if(ret['error']):
            frappe.throw(ret['error'])
        else:
            # frappe.msgprint(str(ret['response']))
            return (ret['response'])

@frappe.whitelist()
def get_shipping_parameter(shop_setting,order_sn):
    # shop_setting = "Crativate dump SHOP"
    # order_sn = '220822RBKE475Y'
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
        path = "/api/v2/logistics/get_shipping_parameter"
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
        frappe.msgprint(str(ret['response']))

        return ret

@frappe.whitelist()
def ship_order(shop_name,addres_id,waktu,order_sn,tracking_no):
    split_time = waktu.split("#")
    frappe.msgprint(str(split_time[1]))
    data = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` where name='{}' """.format(shop_name),as_dict=1)
    for i in data:
        cek = i['seller_test']
        access_token = i['access_token']
        partner_id = i['partner_id']
        partner_key = i['key']
        shop_id = i['shop_id']
        if int(cek) > 0:
            host = "https://partner.test-stable.shopeemobile.com"
        else:
            host = "https://partner.shopeemobile.com"

        timest = int(time.time())
        path = "/api/v2/logistics/ship_order"
        # base_string = partner_id+path+str(timest)+partner_key
        base_string = "%s%s%s%s%s"%(partner_id,path,timest,access_token,shop_id)
        hash_token = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
        url = str(host+path+"?access_token={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,partner_id,shop_id,hash_token,timest))
        # url = "https://partner.shopeemobile.com/api/v2/logistics/ship_order?access_token=access_token&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
        frappe.msgprint(url)
        payload=json.dumps({
            "order_sn": order_sn,
            # "package_number": tracking_no,
            "pickup": {
                "address_id": int(addres_id),
                "pickup_time_id": split_time[1],
                "tracking_number": ""
            }
        })
        headers = {
          'Content-Type': 'application/json'
        }
        #resp = requests.post(url, headers=headers,json=body,allow_redirects=False)
        resp = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
        ret = json.loads(resp.text)
        frappe.msgprint(str(ret))
        frappe.msgprint(str(payload)+"payload")
        return ret

@frappe.whitelist()
def download_shipping_document():
    shop_name = "OpenSANDBOX39454f033ed4e413af6a74fa"
    order_sn = "220830FDM17E5V"
    package_number = "OFG115530027108786"
    data = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` where name='{}' """.format(shop_name),as_dict=1)
    for i in data:
        cek = i['seller_test']
        access_token = i['access_token']
        partner_id = i['partner_id']
        partner_key = i['key']
        shop_id = i['shop_id']
        if int(cek) > 0:
            host = "https://partner.test-stable.shopeemobile.com"
        else:
            host = "https://partner.shopeemobile.com"

        timest = int(time.time())
        path = "/api/v2/logistics/download_shipping_document"
        # base_string = partner_id+path+str(timest)+partner_key
        base_string = "%s%s%s%s%s"%(partner_id,path,timest,access_token,shop_id)
        hash_token = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
        url = str(host+path+"?access_token={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,partner_id,shop_id,hash_token,timest))
        # url = "https://partner.shopeemobile.com/api/v2/logistics/ship_order?access_token=access_token&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
        frappe.msgprint(url)
        payload=json.dumps({
            # "shipping_document_type": "NORMAL_AIR_WAYBILL",
            "order_list": [
                {
                    "order_sn": order_sn,
                    "package_number": package_number
                }
            ]
        })
        headers = {
          'Content-Type': 'application/json'
        }
        #resp = requests.post(url, headers=headers,json=body,allow_redirects=False)
        resp = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
        ret = json.loads(resp.text)
        frappe.msgprint(str(ret))
        frappe.msgprint(str(payload)+"payload")

@frappe.whitelist()
def create_shipping_document(shop_name,order_sn,package_number):
    # https://test-stable.shopee.co.id/product/61000/1810465/
    # shop_name = "OpenSANDBOX39454f033ed4e413af6a74fa"
    # order_sn = "220830FY182THT"
    # package_number = "OFG115548732106865"
    data = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` where name='{}' """.format(shop_name),as_dict=1)
    for i in data:
        cek = i['seller_test']
        access_token = i['access_token']
        partner_id = i['partner_id']
        partner_key = i['key']
        shop_id = i['shop_id']
        if int(cek) > 0:
            host = "https://partner.test-stable.shopeemobile.com"
        else:
            host = "https://partner.shopeemobile.com"

        timest = int(time.time())
        path = "/api/v2/logistics/create_shipping_document"
        # base_string = partner_id+path+str(timest)+partner_key
        base_string = "%s%s%s%s%s"%(partner_id,path,timest,access_token,shop_id)
        hash_token = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
        url = str(host+path+"?access_token={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,partner_id,shop_id,hash_token,timest))
        # url = "https://partner.shopeemobile.com/api/v2/logistics/ship_order?access_token=access_token&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
        frappe.msgprint(url)
        payload=json.dumps({
            # "shipping_document_type": "NORMAL_AIR_WAYBILL",
            "order_list": [
                {
                    "order_sn": order_sn,
                    "package_number": package_number
                }
            ],
        })
        headers = {
          'Content-Type': 'application/json'
        }
        #resp = requests.post(url, headers=headers,json=body,allow_redirects=False)
        resp = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
        ret = json.loads(resp.text)
        frappe.msgprint(str(ret))
        frappe.msgprint(str(payload)+"payload")

@frappe.whitelist()
def batch_ship_order():
    shop_name = "OpenSANDBOX39454f033ed4e413af6a74fa"
    order_sn = "220830FFMB8DD7"
    package_number = "OFG115532186107472"
    data = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` where name='{}' """.format(shop_name),as_dict=1)
    for i in data:
        cek = i['seller_test']
        access_token = i['access_token']
        partner_id = i['partner_id']
        partner_key = i['key']
        shop_id = i['shop_id']
        if int(cek) > 0:
            host = "https://partner.test-stable.shopeemobile.com"
        else:
            host = "https://partner.shopeemobile.com"

        timest = int(time.time())
        path = "/api/v2/logistics/batch_ship_order"
        # base_string = partner_id+path+str(timest)+partner_key
        base_string = "%s%s%s%s%s"%(partner_id,path,timest,access_token,shop_id)
        hash_token = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
        url = str(host+path+"?access_token={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,partner_id,shop_id,hash_token,timest))
        # url = "https://partner.shopeemobile.com/api/v2/logistics/ship_order?access_token=access_token&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
        frappe.msgprint(url)
        payload=json.dumps({
            # "shipping_document_type": "NORMAL_AIR_WAYBILL",
            "order_list": [
                {
                    "order_sn": order_sn
                }
            ],
            "dropoff": {
                "tracking_no": "",
                "branch_id": 0,
                "sender_real_name": ""
            }
        })
        headers = {
          'Content-Type': 'application/json'
        }
        #resp = requests.post(url, headers=headers,json=body,allow_redirects=False)
        resp = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
        ret = json.loads(resp.text)
        frappe.msgprint(str(ret))
        frappe.msgprint(str(payload)+"payload")

@frappe.whitelist()
def get_tracking_number(shop_name,order_sn,package_number):
    # shop_name = "OpenSANDBOX39454f033ed4e413af6a74fa"
    # order_sn = "220831HSSRWTYE"
    # package_number = "OFG115611825109502"
    data = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` where name ='{}' """.format(shop_name),as_dict=1)
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
        path = "/api/v2/logistics/get_tracking_number"
        redirect= "https://google.com"
        base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
        sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
        # url = "https://partner.shopeemobile.com/api/v2/logistics/get_tracking_number?access_token=access_token&order_sn=201214JASXYXY6&package_number=-&partner_id=partner_id&response_optional_fields=first_mile_tracking_number&shop_id=shop_id&sign=sign&timestamp=timestamp"
        url = str(host+path+"?access_token={}&order_sn={}&package_number={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,order_sn,package_number,partner_id,shop_id, sign,timest))
        payload={}
        headers = {

        }
        response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
        ret = json.loads(response.text)
        frappe.msgprint(str(ret))

        return ret

@frappe.whitelist()
def update_shipping_order(shop_name,addres_id,waktu,order_sn,tracking_no):
    split_time = waktu.split("#")
    frappe.msgprint(str(split_time[1]))
    data = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` where name='{}' """.format(shop_name),as_dict=1)
    for i in data:
        cek = i['seller_test']
        access_token = i['access_token']
        partner_id = i['partner_id']
        partner_key = i['key']
        shop_id = i['shop_id']
        if int(cek) > 0:
            host = "https://partner.test-stable.shopeemobile.com"
        else:
            host = "https://partner.shopeemobile.com"

        timest = int(time.time())
        path = "/api/v2/logistics/update_shipping_order"
        # base_string = partner_id+path+str(timest)+partner_key
        base_string = "%s%s%s%s%s"%(partner_id,path,timest,access_token,shop_id)
        hash_token = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
        url = str(host+path+"?access_token={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,partner_id,shop_id,hash_token,timest))
        # url = "https://partner.shopeemobile.com/api/v2/logistics/ship_order?access_token=access_token&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
        frappe.msgprint(url)
        payload=json.dumps({
            "order_sn": order_sn,
            # "package_number": "",
            "pickup": {
                "address_id": int(addres_id),
                "pickup_time_id": split_time[1]
            }
        })
        headers = {
          'Content-Type': 'application/json'
        }
        #resp = requests.post(url, headers=headers,json=body,allow_redirects=False)
        resp = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
        ret = json.loads(resp.text)
        frappe.msgprint(str(ret))
        frappe.msgprint(str(payload)+"payload")
        return ret

@frappe.whitelist()
def cek_status(name,marketplace_id,marketplace):
    if marketplace == 'Shopee':
        cek = frappe.get_doc("Shopee Order",marketplace_id).order_status
        if cek == "PROCESSED":
            frappe.db.sql(""" UPDATE `tabDelivery Note` set cek_pick_up = 1 where name = '{}' """.format(name))
            frappe.db.commit()

