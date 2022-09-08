// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shopee Fake Stock', {
	refresh: function(frm) {
		cur_frm.set_query("item_shopee", function() {
             return {
                 filters: {
                     "type": cur_frm.doc.type,
                     "shopee_setting": cur_frm.doc.shop,
                     "item_code": ['!=',""]
                 }
             }
        });
        cur_frm.set_query("shop", function() {
             return {
                 filters: {
                     "enable_sync":1
                 }
             }
        });
	},
	item_shopee(frm){
		if(cur_frm.doc.item_shopee){
			if(cur_frm.doc.type == "Template"){
				cur_frm.clear_table("item_shopee_variant_fake")
				cur_frm.refresh_field("item_shopee_variant_fake")
				// /home/frappe/frappe-bench/apps/shopee_connector/shopee_connector/shopee_connector/doctype/shopee_fake_stock
				frappe.call({
	                method: "shopee_connector.shopee_connector.doctype.shopee_fake_stock.shopee_fake_stock.ambil_variant",
	                args: {
	                    item_shopee: cur_frm.doc.item_shopee
	                }, callback: function(r) {
	                    console.log(r,"tes si")
	                    for(var i = 0;i<r.message.length;i++){
	                    		var child = cur_frm.add_child("item_shopee_variant_fake");
	                            frappe.model.set_value(child.doctype, child.name, "model_id", r.message[i].model_id)
	                            frappe.model.set_value(child.doctype, child.name, "item_code", r.message[i].item_code)
	                            frappe.model.set_value(child.doctype, child.name, "item_name", r.message[i].item_name)
	                    	}
	                    cur_frm.refresh_field("item_shopee_variant_fake")
	                    // if(r.message){

	                    // }
	                }
	            });	
			}
		}else{
			cur_frm.clear_table("item_shopee_variant_fake")
			cur_frm.refresh_field("item_shopee_variant_fake")
		}
	}
});
