import hmac
import hashlib
import json
import os
import requests
import time

import frappe

@frappe.whitelist()
def mediaspace_upload_img_shopee(cek,partner_id,partner_key,image_path):    
    pathFile = 'demo.solubis.id/public'+image_path
    timest = int(time.time())
    if int(cek) > 0:
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
		('image',('image',open(pathFile,'rb'),'application/octet-stream')) # Replace with actual file path
    ]
    headers = {

	}
    response = requests.request("POST",url,headers=headers, data=payload, files=files, allow_redirects=False)
    ret = json.loads(response.text)
    if(ret['error']):
        frappe.throw(''+str(ret['error']))
    else:		
        return (ret['response']['image_info']['image_id'])