import hmac
import hashlib
import json
import os
import requests
import time

import frappe

@frappe.whitelist()
def update_price(cek,access_token,partner_id,partner_key,shop_id,data):        
    timest = int(time.time())
    language = "id"
    if int(cek) > 0:
        host = "https://partner.test-stable.shopeemobile.com"
    else:
        host = "https://partner.shopeemobile.com"
    path = "/api/v2/product/update_price"
    redirect= "https://google.com"
    base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
    sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
    url = str(host+path+"?access_token={}&language={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,language,partner_id,shop_id, sign,timest))
    payload=json.dumps(data)
    headers = {
		'Content-Type': 'application/json'
	}
    resp = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
    ret = json.loads(resp.text)
	# frappe.msgprint(str(url))
    frappe.msgprint(str(ret))