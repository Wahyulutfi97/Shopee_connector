import hmac
import hashlib
import json
import os
import requests
import time

import frappe

class Brand():
    @frappe.whitelist()
    def get_brand_list_in_category(cek,access_token,partner_id,partner_key,shop_id,offset,idCategory):        
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