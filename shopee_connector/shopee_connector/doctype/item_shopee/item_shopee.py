# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt
from unicodedata import category
import frappe
from frappe.model.document import Document
from shopee_connector.api.logistic import Logistic
from shopee_connector.api.attribute import Attribute

from shopee_connector.api.brand import Brand

from shopee_connector.api.mediaspace import mediaspace_upload_img_shopee
from shopee_connector.api.product import add_item_erp_to_shopee, update_item_erp_to_shopee, add_item_variant_erp_to_shopee, update_item_variant_erp_to_shopee, get_item_base_info, get_model_list, update_stock_item_api

from frappe.utils.background_jobs import enqueue

import re

import ast
import json
import time
import hmac
import hashlib
import requests

class ItemShopee(Document):	
	def validate(self):
		if(self.item_code):
			if(self.item_id):
				# UPDATE PRODUCT SELALU DIJALANKAN KETIKA UPDATE APAPUN doc.type NYA
				self.update_product()									
			else:
				item_id = self.add_product()
				# frappe.msgprint(str(item_id)+" ITEM ID")
				self.item_id = item_id															

	def on_update(self):
		if(self.item_code):
			if(self.type=="Template"):
				if(self.variation_table[0].model_id==""):						
					model_id_list = self.add_item_variant()
					# frappe.msgprint(str(model_id_list)+"MODEL LIST")

					dictVariant = {}
					dictStock = {}
					if model_id_list:
						for i in model_id_list:
							dictVariant[str(i['tier_index'])] = i['model_id']
							dictStock[str(i['tier_index'])] = i['seller_stock'][0]['stock']					

					for itemVariation in self.variation_table:						
						if (self.name_variation_1 and self.name_variation_2):									
							key = [int(itemVariation.id_variation_1), int(itemVariation.id_variation_2)]							
							if str(key) in dictVariant:
								itemVariation.model_id = dictVariant[str(key)]
								itemVariation.stock = dictStock[str(key)]
								itemVariation.save()
								# itemVariation.db_update()
						elif (self.name_variation_1 and not self.name_variation_2):								
							key = [int(itemVariation.id_variation_1)]
							# frappe.msgprint(str(dictVariant)+" DICT")
							# frappe.msgprint(str(key)+" KEY")
							if str(key) in dictVariant:									
								itemVariation.model_id = dictVariant[str(key)]
								itemVariation.stock = dictStock[str(key)]
								itemVariation.save()
				else:				
					cek = frappe.db.sql(""" SELECT * from `tabTable Variation` where parent='{}' order by idx asc""".format(self.name),as_dict=1)
					cekIfUpdate = frappe.db.sql(""" SELECT * from `tabTable Variation` where parent='{}' and model_id IS NOT NULL order by idx asc""".format(self.name),as_dict=1)

					if(len(cek)==len(cekIfUpdate)):
						self.update_item_variant()
					else:
						frappe.msgprint(str('Format Variation Table is not consistent.'))

	@frappe.whitelist()
	def get_logistic(self):
		data = frappe.db.sql(""" SELECT * from `tabShopee Setting` where name = '{}' """.format(self.shopee_setting),as_dict=1)
		for i in data:
			seller_test = i['seller_test']
			listLogistic = Logistic.get_channel_list(i['seller_test'],i['access_token'],i['partner_id'],i['key'],i['shop_id'])

		self.set('losgistic_table', [])
		for logisticnya in listLogistic['logistics_channel_list']:
			if(not seller_test):
				if(logisticnya['enabled']==True):
					if(len(str(logisticnya['logistics_channel_id']))==4):
						row = self.append('losgistic_table', {})
						row.logistic_id = logisticnya['logistics_channel_id']
						row.logistic_name = logisticnya['logistics_channel_name']
						row.enabled = 0
			else:
				if(logisticnya['enabled']==True):
					row = self.append('losgistic_table', {})
					row.logistic_id = logisticnya['logistics_channel_id']
					row.logistic_name = logisticnya['logistics_channel_name']
					row.enabled = 0

	@frappe.whitelist()
	def get_all_variant(self):
		if self.name_variation_1 and not self.name_variation_2:
			tmp=[]
			tmp_cek=[]
			idx_1 = 0
			for i in self.variation_1:				
				tmp.append([i.option,idx_1])					
				idx_1 += 1

			cek = frappe.db.sql(""" SELECT * from `tabTable Variation` where parent='{}' order by idx asc""".format(self.name),as_dict=1)
			if cek:
				for c in cek:
					tmp_cek.append([c['model_id'],c['variation_1'],c['item_code']])
					tmp_cek.append([c['model_id'],c['variation_1'],c['item_code'],c['id_variation_1']])

			output =[]
			for t in tmp:
				count = 0

				for tc in tmp_cek:
					if str(t[0]) == str(tc[1]):
						count = count + 1
				if count < 1:
					# frappe.msgprint('iya')
					tgv2 = {
							'model_id':'',
							'variation_1': t[0],
							# 'variation_2': t[1],
							'item_code': '',
							'id_variation_1' : t[1],
					}
					output.append(tgv2)
				else:
					# frappe.msgprint('tidak')
					child = frappe.db.sql(""" SELECT model_id,variation_1,variation_2,item_code,bobot,model_sku,id_variation_1 from `tabTable Variation` where parent='{}' and variation_1="{}" """.format(self.name,t[0]),as_list=1)
					tgv = {
							'model_id':child[0][0],
							'variation_1': child[0][1],
							# 'variation_2': child[0][2],
							'item_code': child[0][3],
							'bobot': child[0][4],
							'model_sku': child[0][5],
							'id_variation_1' : child[0][6],
					}
					# frappe.msgprint(str(tgv))
					output.append(tgv)
			self.variation_table = []
			for o in output:
				self.append("variation_table",o)

		if self.name_variation_1 and self.name_variation_2:
			tmp=[]
			tmp_cek=[]
			idx_1 = 0
			for i in self.variation_1:
				idx_2 = 0
				for j in self.variation_2:
					tmp.append([i.option,j.option,idx_1,idx_2])
					idx_2 += 1
				idx_1 += 1

			cek = frappe.db.sql(""" SELECT * from `tabTable Variation` where parent='{}' order by idx asc""".format(self.name),as_dict=1)
			if cek:
				for c in cek:
					tmp_cek.append([c['model_id'],c['variation_1'],c['variation_2'],c['item_code'],c['id_variation_1'],c['id_variation_2']])

			output =[]
			for t in tmp:
				count = 0

				for tc in tmp_cek:
					if str(str(t[2])+','+str(t[3])) == str(tc[4]+','+tc[5]):
						count = count + 1
				if count < 1:
					# frappe.msgprint('iya')
					# child = frappe.db.sql(""" SELECT model_id,variation_1,variation_2,item_code,bobot from `tabTable Variation` where parent='{}' and id_variation_1="{}" and id_variation_2 = '{}' """.format(self.name,str(t[2]),str(t[3])),as_list=1)
					tgv2 = {
							# 'model_id':child[0][0],
							'variation_1': t[0],
							'variation_2': t[1],
							'id_variation_1' : t[2],
							'id_variation_2' : t[3],
							# 'item_code': child[0][3],
							# 'bobot': child[0][4]
					}
					output.append(tgv2)
				else:
					# frappe.msgprint('tidak')
					child = frappe.db.sql(""" SELECT model_id,variation_1,variation_2,item_code,bobot,model_sku,id_variation_1,id_variation_2 from `tabTable Variation` where parent='{}' and id_variation_1="{}" and id_variation_2 = '{}' """.format(self.name,str(t[2]),str(t[3])),as_list=1)
					tgv = {
							'model_id':child[0][0],
							'variation_1': t[0],
							'variation_2': t[1],
							'item_code': child[0][3],
							'bobot': child[0][4],
							'model_sku': child[0][5],
							'id_variation_1' : child[0][6],
							'id_variation_2' : child[0][7]
					}
					# frappe.msgprint(str(tgv))
					output.append(tgv)
			self.variation_table = []
			for o in output:
				self.append("variation_table",o)

	@frappe.whitelist()
	def enqueue_brand(self):
		enqueue(self.update_brand_using_category_id, queue="long")

	@frappe.whitelist()
	def update_brand_using_category_id(self):
		idCategory = self.child_4 if self.child_4 else self.child_3 if self.child_3 else self.child_2 if self.child_2 else self.child_1

		data = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE name = '{}' """.format(self.shopee_setting),as_dict=1)
		for i in data:
			saller_test = i['seller_test']
			acces_token = i['access_token']
			partner_id = i['partner_id']
			key = i['key']
			shop_id = i['shop_id']

		brand = Brand.get_brand_list_in_category(saller_test, acces_token, partner_id, key, shop_id, 0,idCategory)		

		count = 1
		while count > 0:
			if brand['error'] == "":
				tmp = []
				for t in brand['response']['brand_list']:
					tmp.append(t)
				for i in tmp:
					if frappe.db.exists("Shopee Brand List",i['brand_id']):
						doc = frappe.get_doc('Shopee Brand List', i['brand_id'])

						temp = ast.literal_eval(doc.use_in_category_id)
						if(idCategory in temp):
							pass
						else:
							temp.append(idCategory)
							doc.use_in_category_id = str(temp)

							doc.save()
					else:
						doc = frappe.new_doc("Shopee Brand List")
						doc.brand_id = i['brand_id']
						doc.original_brand_name = i['original_brand_name']
						doc.display_brand_name = i['display_brand_name']

						temp = []
						temp.append(idCategory)
						doc.use_in_category_id = str(temp)

						doc.flags.ignore_permissions=True
						doc.save()
				if brand['response']['has_next_page'] == True:
					count = 1
					next_offset = brand['response']['next_offset']
					brand = Brand.get_brand_list_in_category(saller_test, acces_token, partner_id, key, shop_id,next_offset,idCategory)
				else:
					count = 0
					break
			else:
				count = 0
				break		

	@frappe.whitelist()
	def add_item_variant(self):
		shopeesetting = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE name = '{}' """.format(self.shopee_setting),as_dict=1)
		for i in shopeesetting:
			saller_test = i['seller_test']
			acces_token = i['access_token']
			partner_id = i['partner_id']
			key = i['key']
			shop_id = i['shop_id']
			price_list = i['price_list']

		data = {}

		# ITEM ID
		data['item_id'] = int(self.item_id)
		# END ITEM ID

		# MODEL
		model_value = []						
		temp_dict_image_variant_tier_1 = {}
		for modelnya in self.variation_table:
			# GET ITEMS PRICE
			doc_item_price = frappe.get_doc('Item Price',{'item_code': modelnya.item_code,'price_list': price_list,"selling":1})
			# END GET ITEMS PRICE

			temp = {}
			# Please use the seller_stock field instead, we will deprecate this field on 2022/10/15
			# temp['normal_stock'] = self.generate_stock_variant(modelnya.item_code, modelnya.bobot)
			temp['original_price'] = doc_item_price.price_list_rate
			if(modelnya.model_sku):
				temp['model_sku'] = modelnya.model_sku			

			tier_index_value = []
			if(self.name_variation_1 and self.name_variation_2):
				tier_index_value.append(int(modelnya.id_variation_1))
				tier_index_value.append(int(modelnya.id_variation_2))
			elif(self.name_variation_1 and not self.name_variation_2):
				tier_index_value.append(int(modelnya.id_variation_1))
			temp['tier_index'] = tier_index_value

			if not modelnya.id_variation_1 in temp_dict_image_variant_tier_1:
				# GET ITEM IN VARIATION TABLE
				doc_item = frappe.get_doc('Item',{'item_code': modelnya.item_code})
				# END GET ITEM

				# imageidlist = []
				# #IMAGE 0
				# imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee))

				# temp_dict_image_variant_tier_1[modelnya.variation_1] = json.dumps(imageidlist)
				# # temp_dict_image_variant_tier_1[modelnya.variation_1] = imageidlist

				if(doc_item.image_shopee):
					#IMAGE 0
					# imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee))					
					temp_dict_image_variant_tier_1[modelnya.variation_1] = mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee)

			# seller_stock
			temp['seller_stock'] = [{				
				"stock": self.generate_stock_variant(modelnya.item_code, modelnya.bobot)
			}]			
			model_value.append(temp)
		data['model'] = model_value
		# END MODEL

		# TIER VARIANT
		tier_variant_value = []

		variant_1 = {}
		variant_1['name'] = self.name_variation_1
		option_list_value = []
		for variant_1_array in self.variation_1:
			temp = {}

			# LANJUTAN temp_dict_image_variant_tier_1
			# if variant_1_array.option in temp_dict_image_variant_tier_1:
			# 	temp['image'] = {"image_id" : temp_dict_image_variant_tier_1[variant_1_array.option]}

			# LANJUTAN temp_dict_image_variant_tier_1
			if variant_1_array.option in temp_dict_image_variant_tier_1:
				temp['image'] = {"image_id" : temp_dict_image_variant_tier_1[variant_1_array.option]}

			temp['option'] = variant_1_array.option

			option_list_value.append(temp)
		variant_1['option_list'] = option_list_value
		tier_variant_value.append(variant_1)

		if(self.variation_2):
			variant_2 = {}
			variant_2['name'] = self.name_variation_2
			option_list_value = []
			for variant_2_array in self.variation_2:
				temp = {}
				temp['option'] = variant_2_array.option

				# KURANG IMAGE DI VARIANT ITEM

				option_list_value.append(temp)
			variant_2['option_list'] = option_list_value
			tier_variant_value.append(variant_2)

		data['tier_variation'] = tier_variant_value
		# END TIER VARIANT

		model_id_item_variant = add_item_variant_erp_to_shopee(saller_test,acces_token,partner_id,key,shop_id,data)		
		return model_id_item_variant

	@frappe.whitelist()
	def update_item_variant(self):
		shopeesetting = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE name = '{}' """.format(self.shopee_setting),as_dict=1)
		for i in shopeesetting:
			saller_test = i['seller_test']
			acces_token = i['access_token']
			partner_id = i['partner_id']
			key = i['key']
			shop_id = i['shop_id']
			price_list = i['price_list']

		# UPDATE
		dataUpdate = {}

		# ITEM ID
		dataUpdate['item_id'] = int(self.item_id)
		# END ITEM ID

		# TIER VARIANT
		tier_variant_value = []

		variant_1 = {}
		variant_1['name'] = self.name_variation_1
		option_list_value = []
		for variant_1_array in self.variation_1:
			temp = {}

			# LANJUTAN temp_dict_image_variant_tier_1
			# if variant_1_array.option in temp_dict_image_variant_tier_1:
			# 	temp['image'] = {"image_id" : temp_dict_image_variant_tier_1[variant_1_array.option]}

			temp['option'] = variant_1_array.option

			option_list_value.append(temp)
		variant_1['option_list'] = option_list_value
		tier_variant_value.append(variant_1)

		if(self.variation_2):
			variant_2 = {}
			variant_2['name'] = self.name_variation_2
			option_list_value = []
			for variant_2_array in self.variation_2:
				temp = {}
				temp['option'] = variant_2_array.option

				# KURANG IMAGE DI VARIANT ITEM

				option_list_value.append(temp)
			variant_2['option_list'] = option_list_value
			tier_variant_value.append(variant_2)

		dataUpdate['tier_variation'] = tier_variant_value
		# END TIER VARIANT

		# MODEL
		model_value = []
		# SHOPEE CONDITION IMAGE IN VARIANT HANYA BOLEH DI TIER 1 : ID of image. You can choose to define or not define the option image. If you choose to define, you can only define an image for the first tier, and you need to define an image for all options of the first tier
		# logic : make dict temp_dict_image_variant_tier_1 -> {variant_1_a : ['image_id1','image_id2','image_id3'], variant_1_a : ['image_id1','image_id2','image_id3']}
		# temp_dict_image_variant_tier_1 dipanggil ketika generate data di loop variant_1_array, jadi isi temp['image_id'] = temp_dict_image_variant_tier_1[variant_1_array.option]
		temp_dict_image_variant_tier_1 = {}
		for modelnya in self.variation_table:
			# frappe.msgprint(str(modelnya.item_code))
			if(modelnya.model_id):
				# GET ITEMS PRICE
				doc_item_price = frappe.get_doc('Item Price',{'item_code': modelnya.item_code,'price_list': price_list,"selling":1})
				# END GET ITEMS PRICE

				temp = {}
				tier_index_value = []
				if(self.name_variation_1 and self.name_variation_2):
					tier_index_value.append(int(modelnya.id_variation_1))
					tier_index_value.append(int(modelnya.id_variation_2))
				elif(self.name_variation_1 and not self.name_variation_2):
					tier_index_value.append(int(modelnya.id_variation_1))				
				temp['tier_index'] = tier_index_value
				temp['model_id'] = int(modelnya.model_id)

				if not modelnya.id_variation_1 in temp_dict_image_variant_tier_1:
					# GET ITEM IN VARIATION TABLE
					doc_item = frappe.get_doc('Item',{'item_code': modelnya.item_code})
					# END GET ITEM

					imageidlist = []
					#IMAGE 0
					imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee))

					temp_dict_image_variant_tier_1[modelnya.variation_1] = json.dumps(imageidlist)
					# temp_dict_image_variant_tier_1[modelnya.variation_1] = imageidlist

				model_value.append(temp)
		dataUpdate['model_list'] = model_value
		# END MODEL
		# END UPDATE
		update_item_variant_erp_to_shopee(saller_test,acces_token,partner_id,key,shop_id,dataUpdate)

	@frappe.whitelist()
	def add_product(self):
		# GET ITEMS FROM ITEM CODE
		doc_item = frappe.get_doc('Item',{'item_code': self.item_code})
		# END GET ITEMS FROM ITEM CODE

		# MEDIASPACE UPLOAD IMAGE IN ITEM
		shopeesetting = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE name = '{}' """.format(self.shopee_setting),as_dict=1)
		for i in shopeesetting:
			saller_test = i['seller_test']
			acces_token = i['access_token']
			partner_id = i['partner_id']
			key = i['key']
			shop_id = i['shop_id']
			price_list = i['price_list']

		data = {}
		data['original_price'] = frappe.get_value("Item Price",{"item_code": self.item_code, 'price_list': price_list}, "price_list_rate") if self.type=='Product' else 99
		
		CLEANR = re.compile('<.*?>') 
		data['description'] = re.sub(CLEANR, '', frappe.get_value("Item",{"name": self.item_code}, "description"))
		data['weight'] = doc_item.weight_per_unit/1000
		data['item_name'] = self.item_name
		dictStock={}
		dictStock['stock'] = self.generate_stock() if self.type=="Product" else 1
		data["seller_stock"] = [dictStock]		
		# data['normal_stock'] = self.generate_stock() if self.type=="Product" else 1
		self.stock = self.generate_stock() if self.type=="Product" else 1

		# LOGISTIC INPUT TO JSON
		tempLogistic = []
		for i in self.losgistic_table:
			if(i.enabled==1):
				logisticDict = {}
				logisticDict['enabled'] = True
				logisticDict['logistic_id'] = int(i.logistic_id)
				tempLogistic.append(logisticDict)
		data['logistic_info'] = tempLogistic
		# END LOGISTIC

		data['item_dangerous'] = 1 if self.item_dangerous == 1 else 0
		# PRE ORDER
		preorder = {}
		preorder['is_pre_order'] = True if self.pre_order == 1 else False
		data['pre_order'] = preorder
		# END PRE ORDER
		data['condition'] = self.condition
		data['item_sku'] = self.item_sku

		# DIMENSION
		dimension = {}
		dimension['package_height'] = doc_item.panjang
		dimension['package_length'] = doc_item.tinggi
		dimension['package_width'] = doc_item.lebar
		data['dimension'] = dimension
		#END DIMENSION

		# ATTRIBUTE LIST
		tempAttribute = []
		for i in self.specifications:
			attribute = {}
			tempAttributeValueList = []
			if(i.input_type=="TEXT_FILED" and i.output):
				attribute['attribute_id'] = int(i.attribute_id)

				attributeValueList = {}
				attributeValueList['value_id'] = 0
				attributeValueList['original_value_name '] = i.output

				if(i.attribute_unit):
					attributeValueList['value_unit'] = i.attribute_unit

				tempAttributeValueList.append(attributeValueList)
				attribute['attribute_value_list'] = tempAttributeValueList

				tempAttribute.append(attribute)
			elif(i.input_type=="COMBO_BOX" and i.value_id):
				attribute['attribute_id'] = int(i.attribute_id)

				attributeValueList = {}
				attributeValueList['value_id'] = int(i.value_id)

				if(i.attribute_unit):
					attributeValueList['value_unit'] = i.attribute_unit

				tempAttributeValueList.append(attributeValueList)
				attribute['attribute_value_list'] = tempAttributeValueList

				tempAttribute.append(attribute)
			elif(i.input_type=="DROP_DOWN" and i.value_id):
				attribute['attribute_id'] = int(i.attribute_id)

				attributeValueList = {}
				attributeValueList['value_id'] = int(i.value_id)

				if(i.attribute_unit):
					attributeValueList['value_unit'] = i.attribute_unit

				tempAttributeValueList.append(attributeValueList)
				attribute['attribute_value_list'] = tempAttributeValueList

				tempAttribute.append(attribute)
			elif(i.input_type=="MULTIPLE_SELECT_COMBO_BOX" and i.value_id):
				attribute['attribute_id'] = int(i.attribute_id)

				attributeValueList = {}
				attributeValueList['value_id'] = int(i.value_id)

				tempAttributeValueList.append(attributeValueList)
				attribute['attribute_value_list'] = tempAttributeValueList

				tempAttribute.append(attribute)

		if(tempAttribute):
			data['attribute_list'] = tempAttribute
		else:
			# frappe.msgprint('Specifications must be filled at least 1!')
			pass
		# END ATTRIBUTE LIST

		# CATEGORY
		data['category_id'] = int(self.child_4 if self.child_4 else self.child_3 if self.child_3 else self.child_2 if self.child_2 else self.child_1)
		# END CATEGORY

		# BRAND
		brand = {}
		brand['brand_id'] = int(self.id_brand)
		data['brand'] = brand
		#END BRAND

		# IMAGE
		tempimage = {}
		imageidlist = []
		#IMAGE 0
		imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee))

		# IMAGE 1
		if(doc_item.image_shopee_1):
			imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_1))

		# IMAGE 2
		if(doc_item.image_shopee_2):
			imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_2))

		# IMAGE 3
		if(doc_item.image_shopee_3):
			imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_3))

		# IMAGE 4
		if(doc_item.image_shopee_4):
			imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_4))

		# IMAGE 5
		if(doc_item.image_shopee_5):
			imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_5))

		# IMAGE 6
		if(doc_item.image_shopee_6):
			imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_6))

		# IMAGE 7
		if(doc_item.image_shopee_7):
			imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_7))

		# IMAGE 8
		if(doc_item.image_shopee_8):
			imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_8))

		tempimage['image_id_list'] = imageidlist
		data['image'] = tempimage
		# END MEDIASPACE UPLOAD IMAGE IN ITEM
		# END IMAGE

		item_id = add_item_erp_to_shopee(saller_test,acces_token,partner_id,key,shop_id,data)
		return item_id

	@frappe.whitelist()
	def update_product(self):
		# GET ITEMS FROM ITEM CODE
		doc_item = frappe.get_doc('Item',{'item_code': self.item_code})
		# END GET ITEMS FROM ITEM CODE

		# MEDIASPACE UPLOAD IMAGE IN ITEM
		shopeesetting = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE name = '{}' """.format(self.shopee_setting),as_dict=1)
		for i in shopeesetting:
			saller_test = i['seller_test']
			acces_token = i['access_token']
			partner_id = i['partner_id']
			key = i['key']
			shop_id = i['shop_id']

		data = {}
		data['item_id'] = int(self.item_id)
		
		CLEANR = re.compile('<.*?>') 
		data['description'] = re.sub(CLEANR, '', frappe.get_value("Item",{"name": self.item_code}, "description"))
		data['weight'] = doc_item.weight_per_unit/1000
		data['item_name'] = self.item_name

		# LOGISTIC INPUT TO JSON
		tempLogistic = []
		for i in self.losgistic_table:
			if(i.enabled==1):
				logisticDict = {}
				logisticDict['enabled'] = True
				logisticDict['logistic_id'] = int(i.logistic_id)
				tempLogistic.append(logisticDict)
		data['logistic_info'] = tempLogistic
		# END LOGISTIC

		data['item_dangerous'] = 1 if self.item_dangerous == 1 else 0
		# PRE ORDER
		preorder = {}
		preorder['is_pre_order'] = True if self.pre_order == 1 else False
		data['pre_order'] = preorder
		# END PRE ORDER
		data['condition'] = self.condition

		# DIMENSION
		dimension = {}
		dimension['package_height'] = doc_item.panjang
		dimension['package_length'] = doc_item.tinggi
		dimension['package_width'] = doc_item.lebar
		data['dimension'] = dimension
		#END DIMENSION

		# ATTRIBUTE LIST
		tempAttribute = []
		for i in self.specifications:
			attribute = {}
			tempAttributeValueList = []
			if(i.input_type=="TEXT_FILED" and i.output):
				attribute['attribute_id'] = int(i.attribute_id)

				attributeValueList = {}
				attributeValueList['value_id'] = 0
				attributeValueList['original_value_name '] = i.output

				if(i.attribute_unit):
					attributeValueList['value_unit'] = i.attribute_unit

				tempAttributeValueList.append(attributeValueList)
				attribute['attribute_value_list'] = tempAttributeValueList

				tempAttribute.append(attribute)
			elif(i.input_type=="COMBO_BOX" and i.value_id):
				attribute['attribute_id'] = int(i.attribute_id)

				attributeValueList = {}
				attributeValueList['value_id'] = int(i.value_id)

				if(i.attribute_unit):
					attributeValueList['value_unit'] = i.attribute_unit

				tempAttributeValueList.append(attributeValueList)
				attribute['attribute_value_list'] = tempAttributeValueList

				tempAttribute.append(attribute)
			elif(i.input_type=="DROP_DOWN" and i.value_id):
				attribute['attribute_id'] = int(i.attribute_id)

				attributeValueList = {}
				attributeValueList['value_id'] = int(i.value_id)

				if(i.attribute_unit):
					attributeValueList['value_unit'] = i.attribute_unit

				tempAttributeValueList.append(attributeValueList)
				attribute['attribute_value_list'] = tempAttributeValueList

				tempAttribute.append(attribute)
			elif(i.input_type=="MULTIPLE_SELECT_COMBO_BOX" and i.value_id):
				attribute['attribute_id'] = int(i.attribute_id)

				attributeValueList = {}
				attributeValueList['value_id'] = int(i.value_id)

				tempAttributeValueList.append(attributeValueList)
				attribute['attribute_value_list'] = tempAttributeValueList

				tempAttribute.append(attribute)

		if(tempAttribute):
			data['attribute_list'] = tempAttribute
		else:
			# frappe.msgprint('Specifications must be filled at least 1!')
			pass
		# END ATTRIBUTE LIST
		
		# CATEGORY
		data['category_id'] = int(self.child_4 if self.child_4 else self.child_3 if self.child_3 else self.child_2 if self.child_2 else self.child_1)
		# END CATEGORY

		# BRAND
		brand = {}
		brand['brand_id'] = int(self.id_brand)
		data['brand'] = brand
		#END BRAND

		if(self.update_image):
			# IMAGE
			tempimage = {}
			imageidlist = []
			#IMAGE 0
			imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee))

			# IMAGE 1
			if(doc_item.image_shopee_1):
				imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_1))

			# IMAGE 2
			if(doc_item.image_shopee_2):
				imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_2))

			# IMAGE 3
			if(doc_item.image_shopee_3):
				imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_3))

			# IMAGE 4
			if(doc_item.image_shopee_4):
				imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_4))

			# IMAGE 5
			if(doc_item.image_shopee_5):
				imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_5))

			# IMAGE 6
			if(doc_item.image_shopee_6):
				imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_6))

			# IMAGE 7
			if(doc_item.image_shopee_7):
				imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_7))

			# IMAGE 8
			if(doc_item.image_shopee_8):
				imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee_8))

			tempimage['image_id_list'] = imageidlist
			data['image'] = tempimage
			# END MEDIASPACE UPLOAD IMAGE IN ITEM
			# END IMAGE

		update_item_erp_to_shopee(saller_test,acces_token,partner_id,key,shop_id,data)

		if(self.type=="Product"):			
			test = get_item_base_info(saller_test,acces_token,partner_id,key,shop_id,self.item_id)['response']['item_list'][0]['stock_info_v2']['seller_stock'][0]['stock'] if len(get_item_base_info(saller_test,acces_token,partner_id,key,shop_id,self.item_id)['response']['item_list'][0]['stock_info_v2']) > 1 else 0			
			stocknya = test if self.is_fake else self.generate_stock()
			payloadUpdate = {
				"item_id":int(self.item_id),
				"stock_list": [
					{
					"model_id": 0,
					"seller_stock": [
						{
						"location_id": "",
						"stock": stocknya
						}
					]
					},
				]
			}					
			update_stock_item_api(saller_test,acces_token,partner_id,key,shop_id,payloadUpdate)
			self.stock = stocknya
		else:			
			if(self.variation_table[0].model_id!=""):
				# frappe.msgprint(str(self.variation_table[0].model_id))
				stock_list = []
				test = get_model_list(saller_test, acces_token, partner_id,key, shop_id, self.item_id)
				# frappe.msgprint(str(test)+" response get model list")
				dictModelIdStock = {}
				for x in test['response']['model']:
					# frappe.msgprint(str(x)+" for get model list")					
					dictModelIdStock[x['model_id']] = x['stock_info_v2']['seller_stock'][0]['stock'] if len(x['stock_info_v2']) > 1 else 0
				
				for i in self.variation_table:								
					stocknya = dictModelIdStock[int(i.model_id)] if i.is_fake else self.generate_stock_variant(i.item_code,i.bobot)
					tempDict = {
						"model_id" : int(i.model_id),
						"seller_stock" : [
							{
								"location_id": "",
								"stock": stocknya
							}
						]
					}
					i.stock = stocknya
					stock_list.append(tempDict)

				payloadUpdate = {
					"item_id":int(self.item_id),
					"stock_list":stock_list
				}
				
				update_stock_item_api(saller_test,acces_token,partner_id,key,shop_id,payloadUpdate)		

	@frappe.whitelist()
	def generate_stock(self):
		warehouse = frappe.get_value("Shopee Setting",{"name": self.shopee_setting}, "warehouse")
		stock = frappe.get_value("Bin",{"item_code": self.item_code,"warehouse":warehouse}, "projected_qty")
		get_bobot = frappe.db.sql(""" SELECT bobot,name from `tabItem Shopee` where item_code = '{}' """.format(self.item_code),as_list=1)
		# frappe.msgprint(str(get_bobot)+" Get bobot sql")
		tmp_bobot = []		
		if get_bobot:
			for i in get_bobot:
				tmp_bobot.append(i[0])

		if len(tmp_bobot) > 0:
			nilai_bobot = sum(tmp_bobot)
		else:
			nilai_bobot = self.bobot

		if stock:			
			bagi = (stock*(self.bobot / (nilai_bobot)))
		else:			
			if self.type == "Product":
				frappe.msgprint("Stock "+self.item_code+" Not in warehouse "+warehouse+" !")
			bagi = 0

		# frappe.msgprint(str(int(round(bagi, 0)))+" STOCK AKHIR")
		return int(round(bagi, 0))

	@frappe.whitelist()
	def generate_stock_variant(self, item_code_variant,bobot_variant):
		warehouse = frappe.get_value("Shopee Setting",{"name": self.shopee_setting}, "warehouse")
		stock = frappe.get_value("Bin",{"item_code": item_code_variant,"warehouse":warehouse}, "projected_qty")
		get_bobot = frappe.db.sql(""" SELECT bobot from `tabTable Variation` where item_code = '{}' """.format(item_code_variant),as_list=1)

		tmp_bobot = []		
		if get_bobot:
			for i in get_bobot:
				tmp_bobot.append(i[0])

		if len(tmp_bobot) > 0:
			nilai_bobot = sum(tmp_bobot)
		else:
			nilai_bobot = bobot_variant

		if stock:
			bagi = (stock*(bobot_variant / (nilai_bobot)))
		else:
			if self.type == "Product":
				frappe.msgprint("Stock "+item_code_variant+" Not in warehouse "+warehouse+" !")
			bagi = 0

		# frappe.msgprint(str(int(round(bagi, 0)))+" STOCK AKHIR VARIANT")
		return int(round(bagi, 0))

	@frappe.whitelist()
	def test(self):
		shopeesetting = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE name = '{}' """.format(self.shopee_setting),as_dict=1)
		for i in shopeesetting:
			saller_test = i['seller_test']
			acces_token = i['access_token']
			partner_id = i['partner_id']
			key = i['key']
			shop_id = i['shop_id']
			price_list = i['price_list']

		data = {}

		# ITEM ID
		data['item_id'] = int(self.item_id)
		# END ITEM ID

		# MODEL
		model_value = []						
		temp_dict_image_variant_tier_1 = {}
		for modelnya in self.variation_table:
			# GET ITEMS PRICE
			doc_item_price = frappe.get_doc('Item Price',{'item_code': modelnya.item_code,'price_list': price_list,"selling":1})
			# END GET ITEMS PRICE

			temp = {}
			# Please use the seller_stock field instead, we will deprecate this field on 2022/10/15
			# temp['normal_stock'] = self.generate_stock_variant(modelnya.item_code, modelnya.bobot)
			temp['original_price'] = doc_item_price.price_list_rate
			if(modelnya.model_sku):
				temp['model_sku'] = modelnya.model_sku			

			tier_index_value = []
			if(self.name_variation_1 and self.name_variation_2):
				tier_index_value.append(int(modelnya.id_variation_1))
				tier_index_value.append(int(modelnya.id_variation_2))
			elif(self.name_variation_1 and not self.name_variation_2):
				tier_index_value.append(int(modelnya.id_variation_1))
			temp['tier_index'] = tier_index_value

			if not modelnya.id_variation_1 in temp_dict_image_variant_tier_1:
				# GET ITEM IN VARIATION TABLE
				doc_item = frappe.get_doc('Item',{'item_code': modelnya.item_code})
				# END GET ITEM

				# imageidlist = []
				if(doc_item.image_shopee):
					#IMAGE 0
					# imageidlist.append(mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee))					
					temp_dict_image_variant_tier_1[modelnya.variation_1] = mediaspace_upload_img_shopee(saller_test,partner_id,key,doc_item.image_shopee)

			# seller_stock
			temp['seller_stock'] = [{				
				"stock": self.generate_stock_variant(modelnya.item_code, modelnya.bobot)
			}]			
			model_value.append(temp)
		data['model'] = model_value
		# END MODEL

		# TIER VARIANT
		tier_variant_value = []

		variant_1 = {}
		variant_1['name'] = self.name_variation_1
		option_list_value = []
		for variant_1_array in self.variation_1:
			temp = {}

			# LANJUTAN temp_dict_image_variant_tier_1
			if variant_1_array.option in temp_dict_image_variant_tier_1:
				temp['image'] = {"image_id" : temp_dict_image_variant_tier_1[variant_1_array.option]}

			temp['option'] = variant_1_array.option

			option_list_value.append(temp)
		variant_1['option_list'] = option_list_value
		tier_variant_value.append(variant_1)

		if(self.variation_2):
			variant_2 = {}
			variant_2['name'] = self.name_variation_2
			option_list_value = []
			for variant_2_array in self.variation_2:
				temp = {}
				temp['option'] = variant_2_array.option

				# KURANG IMAGE DI VARIANT ITEM

				option_list_value.append(temp)
			variant_2['option_list'] = option_list_value
			tier_variant_value.append(variant_2)

		data['tier_variation'] = tier_variant_value
		# END TIER VARIANT

		frappe.msgprint(str(data))