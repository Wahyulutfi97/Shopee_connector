// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Get Order', {
	refresh: function(frm) {

	},
	get_order(frm){
		frappe.call({
                 method: "shopee_connector.api.order.get_order_list_ulang",
                 args: {
                 	tanggal: cur_frm.doc.date,
                 	shop: cur_frm.doc.shop
                 },
                 callback: function(r) {
                    
                }
        });
	}
});
