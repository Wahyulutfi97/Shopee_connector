# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt
from unicodedata import category
import frappe
from frappe.model.document import Document
from shopee_connector.api.logistic import Logistic
from shopee_connector.api.attribute import Attribute

from shopee_connector.api.brand import Brand

from shopee_connector.api.mediaspace import mediaspace_upload_img_shopee

import ast
import json
import time
import hmac
import hashlib
import requests

class ItemShopee(Document):
	def validate(self):
		if(self.item_id):
			self.update_product()
			# model_id_list = self.add_item_variant()
			# if(self.type=="Template"):
			# 	model_id_list = self.add_item_variant()
			# 	# frappe.msgprint(str(model_id_list))
			# 	for i in model_id_list:
			# 		cek = frappe.db.sql(""" SELECT * from `tabTable Variation` where parent='{}' and id_variation_1='{}' and id_variation_2='{}' """.format(self.name,i.tier_index[0], i.tier_index[1]),as_dict=1)
			# 		test = frappe.get_doc('Table Variation', cek[0]['name'])
			# 		test.model_id =  i.model_id
			# 		test.save()
		else:
			item_id = self.add_product()
			# product > get_item_base_info = update stock
			# get_item_to_erp
			self.item_id = item_id

			# if(self.type=="Template"):
			# 	model_id_list = self.add_item_variant()
			# 	for i in model_id_list:
			# 		frappe.msgprint(str(i['tier_index'][0]))
			# 		frappe.msgprint(str(i['tier_index'][1]))
			# 		cek = frappe.db.sql(""" SELECT * from `tabTable Variation` where parent='{}' and id_variation_1='{}' and id_variation_2='{}' """.format(self.name,i['tier_index'][0], i['tier_index'][1]),as_dict=1)
			# 		frappe.throw(str(cek))
			# 		test = frappe.get_doc('Table Variation', cek[0]['name'])
			# 		test.model_id =  i.model_id
			# 		test.save()

	def after_insert(self):
		if(self.type=="Template"):
			model_id_list = self.add_item_variant()			
			for i in model_id_list:
				frappe.msgprint(str(i['tier_index'][0]))
				frappe.msgprint(str(i['tier_index'][1]))
				cek = frappe.db.sql(""" SELECT * from `tabTable Variation` where parent='{}' and id_variation_1='{}' and id_variation_2='{}' """.format(self.name,i['tier_index'][0], i['tier_index'][1]),as_dict=1)
				frappe.msgprint(str(cek))
				test = frappe.get_doc('Table Variation', cek[0]['name'])
				test.model_id =  i['model_id']
				test.save()


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
		idx_v_1 = 0
		for variant_1 in self.variation_1:
			if(self.variation_2):
				idx_v_2 = 0
				for variant_2 in self.variation_2:
					row = self.append('variation_table', {})
					row.variation_1 = variant_1.option
					row.id_variation_1 = idx_v_1
					row.variation_2 = variant_2.option
					row.id_variation_2 = idx_v_2

					idx_v_2+=1
			else:
				row = self.append('variation_table', {})
				row.variation_1 = variant_1.option
				row.id_variation_1 = idx_v_1
			idx_v_1+=1

	# @frappe.whitelist()
	# def get_specifications(self):
	# 	data = frappe.db.sql(""" SELECT * FROM `tabShopee Setting` WHERE name = '{}' """.format(self.shopee_setting),as_dict=1)
	# 	category_id = self.child_4 if self.child_4 else self.child_3 if self.child_3 else self.child_2 if self.child_2 else self.child_1
	# 	for i in data:
	# 		listAttribute = Attribute.get_attribute_list(i['seller_test'],i['access_token'],i['partner_id'],i['key'],i['shop_id'],category_id)

	# 	self.set('specifications', [])
	# 	for attributenya in listAttribute['attribute_list']:
	# 		row = self.append('specifications', {})
	# 		row.attribute_id = attributenya['attribute_id']
	# 		row.display_name = attributenya['display_attribute_name']
	# 		row.input_type = attributenya['input_type']

	# 	frappe.msgprint(str(listAttribute))
	# 	frappe.msgprint('Metod gak terpakai, pindah ke .js')

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
		frappe.msgprint('Update brand list successful!')

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
		# SHOPEE CONDITION IMAGE IN VARIANT HANYA BOLEH DI TIER 1 : ID of image. You can choose to define or not define the option image. If you choose to define, you can only define an image for the first tier, and you need to define an image for all options of the first tier
		# logic : make dict temp_dict_image_variant_tier_1 -> {variant_1_a : ['image_id1','image_id2','image_id3'], variant_1_a : ['image_id1','image_id2','image_id3']}
		# temp_dict_image_variant_tier_1 dipanggil ketika generate data di loop variant_1_array, jadi isi temp['image_id'] = temp_dict_image_variant_tier_1[variant_1_array.option]
		temp_dict_image_variant_tier_1 = {}
		for modelnya in self.variation_table:
			# GET ITEMS PRICE
			doc_item_price = frappe.get_doc('Item Price',{'item_code': modelnya.item_code,'price_list': price_list,"selling":1})
			# END GET ITEMS PRICE

			temp = {}
			temp['normal_stock'] = generate_stock_variant(modelnya.item_code)
			temp['original_price'] = doc_item_price.price_list_rate
			temp['model_sku'] = modelnya.model_sku

			tier_index_value = []
			tier_index_value.append(int(modelnya.id_variation_1))
			tier_index_value.append(int(modelnya.id_variation_2))
			temp['tier_index'] = tier_index_value

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

		dataPayload = json.dumps(data)
		# frappe.throw(str(dataPayload))
		frappe.msgprint(str(dataPayload))
		# frappe.msgprint('awuuuu')
		model_id_item_variant = add_item_variant_erp_to_shopee(saller_test,acces_token,partner_id,key,shop_id,data)
		return model_id_item_variant

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
		data['original_price'] = frappe.get_value("Item Price",{"item_code": self.item_code}, "price_list_rate") if self.type=='Product' else 99
		data['description'] = frappe.get_value("Item",{"name": self.item_code}, "description")
		data['weight'] = doc_item.weight_per_unit
		data['item_name'] = self.item_name
		data['normal_stock'] = self.generate_stock()

		# LOGISTIC INPUT TO JSON
		tempLogistic = []
		for i in self.losgistic_table:
			if(i.enabled==1):
				logisticDict = {}
				logisticDict['enabled'] = True
				logisticDict['logistic_id'] = i.logistic_id
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
			frappe.msgprint('Specifications must be filled at least 1!')
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

		dataPayload = json.dumps(data)
		# frappe.throw(str(dataPayload))
		frappe.msgprint(str(dataPayload))
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
		data['description'] = frappe.get_value("Item",{"name": self.item_code}, "description")
		data['weight'] = doc_item.weight_per_unit
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
			frappe.msgprint('Specifications must be filled at least 1!')
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

		# dataPayload = json.dumps(data)
		# frappe.throw(str(dataPayload))
		# frappe.msgprint(str(dataPayload))
		update_item_erp_to_shopee(saller_test,acces_token,partner_id,key,shop_id,data)

	@frappe.whitelist()
	def generate_stock(self):
		warehouse = frappe.get_value("Shopee Setting",{"name": self.shopee_setting}, "warehouse")		
		stock = frappe.get_value("Bin",{"item_code": self.item_code,"warehouse":warehouse}, "projected_qty")
		get_bobot = frappe.db.sql(""" SELECT bobot from `tabItem Shopee` where item_code = '{}' """.format(self.item_code),as_list=1)				

		tmp_bobot = []
		tmp_bobot.append(self.bobot)		
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

		return int(round(bagi, 0))
	
	@frappe.whitelist()
	def generate_stock_variant(self, item_code_variant):
		warehouse = frappe.get_value("Shopee Setting",{"name": self.shopee_setting}, "warehouse")		
		stock = frappe.get_value("Bin",{"item_code": item_code_variant,"warehouse":warehouse}, "projected_qty")
		get_bobot = frappe.db.sql(""" SELECT bobot from `tabTable Variation` where item_code = '{}' """.format(item_code_variant),as_list=1)				

		tmp_bobot = []
		tmp_bobot.append(self.bobot)		
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
				frappe.msgprint("Stock "+item_code_variant+" Not in warehouse "+warehouse+" !")
			bagi = 0

		return int(round(bagi, 0))

	@frappe.whitelist()
	def test(self):
		warehouse = frappe.get_value("Shopee Setting",{"name": self.shopee_setting}, "warehouse")
		frappe.msgprint(str(warehouse))
		stock = frappe.get_value("Bin",{"item_code": self.item_code,"warehouse":warehouse}, "projected_qty")
		frappe.msgprint(str(stock))
		get_bobot = frappe.db.sql(""" SELECT bobot from `tabItem Shopee` where item_code = '{}' """.format(self.item_code),as_list=1)		
		frappe.msgprint(str(get_bobot))

		tmp_bobot = []
		tmp_bobot.append(self.bobot)		
		if get_bobot:
			for i in get_bobot:
				tmp_bobot.append(i[0])

		frappe.msgprint(str(tmp_bobot))
		if len(tmp_bobot) > 0:
			nilai_bobot = sum(tmp_bobot)
		else:
			nilai_bobot = self.bobot

		frappe.msgprint(str(nilai_bobot))
		if stock:
			bagi = (stock*(self.bobot / (nilai_bobot)))
			frappe.msgprint("("+str(stock)+"("+str(self.bobot)+" / "+str(nilai_bobot)+")")
		else:
			if self.type == "Product":
				frappe.msgprint("Stock "+self.item_code+" Not in warehouse "+warehouse+" !")
			bagi = 0

		frappe.msgprint(str(bagi))

		frappe.msgprint(str(int(round(bagi, 0))))

@frappe.whitelist()
def add_item_erp_to_shopee(cek,access_token,partner_id,partner_key,shop_id,data):
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
	payload=json.dumps(data)

	headers = {
		'Content-Type': 'application/json'
	}

	resp = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
	ret = json.loads(resp.text)
	# frappe.msgprint(str(url))
	frappe.msgprint(str(ret))
	return ret['response']['item_id']

@frappe.whitelist()
def update_item_erp_to_shopee(cek,access_token,partner_id,partner_key,shop_id,data):
	timest = int(time.time())
	language = "id"
	if int(cek) > 0:
		host = "https://partner.test-stable.shopeemobile.com"
	else:
		host = "https://partner.shopeemobile.com"
	path = "/api/v2/product/update_item"
	redirect= "https://google.com"
	base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
	sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	url = str(host+path+"?access_token={}&language={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,language,partner_id,shop_id, sign,timest))
	payload=json.dumps(data)

	resp = requests.request("POST",url, data=payload, allow_redirects=False)
	ret = json.loads(resp.text)
	frappe.msgprint(str(ret))

@frappe.whitelist()
def add_item_variant_erp_to_shopee(cek,access_token,partner_id,partner_key,shop_id,data):
	timest = int(time.time())
	if int(cek) > 0:
		host = "https://partner.test-stable.shopeemobile.com"
	else:
		host = "https://partner.shopeemobile.com"
	path = "/api/v2/product/init_tier_variation"
	redirect= "https://google.com"
	base_string = "%s%s%s%s%s"%(partner_id, path, timest,access_token,shop_id )
	sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	# url = "https://partner.shopeemobile.com/api/v2/product/init_tier_variation?access_token=access_token&partner_id=partner_id&shop_id=shop_id&sign=sign&timestamp=timestamp"
	url = str(host+path+"?access_token={}&partner_id={}&shop_id={}&sign={}&timestamp={}".format(access_token,partner_id,shop_id, sign,timest))
	payload=json.dumps(data)

	resp = requests.request("POST",url, data=payload, allow_redirects=False)
	ret = json.loads(resp.text)
	frappe.msgprint(str(ret))
	return ret['response']['model']
	# frappe.throw(str(ret))
