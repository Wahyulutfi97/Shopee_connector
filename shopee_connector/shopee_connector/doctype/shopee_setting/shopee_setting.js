// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shopee Setting', {
	refresh: function(frm) {

	},
	get_product(frm){
		// frappe.msgprint("tes")
		frappe.call({
                 method: "shopee_connector.api.product.get_item_list_ulang",
                 args: {
                 	   name: cur_frm.doc.name,
                 	   cek: cur_frm.doc.seller_test,
                     access_token: cur_frm.doc.access_token,
                     partner_id: cur_frm.doc.partner_id,
                     partner_key: cur_frm.doc.key,
                     shop_id: cur_frm.doc.shop_id
                 },
                 callback: function(r) {
                    
                }
        });
	}
});
