frappe.ui.form.on('Delivery Note', {
	refresh(frm) {
		// your code here
        frappe.call({
            method: "shopee_connector.api.logistic.cek_status", 
            args: {
                name: cur_frm.doc.name,
                marketplace_id: cur_frm.doc.marketplace_id,
                marketplace: cur_frm.doc.marketplace
            },
            callback: function(r) {
                // console.log(r)
            }
        })
	},
    update_shipping_order(frm){
        frappe.msgprint('tes')
        frappe.call({method:'shopee_connector.api.logistic.get_shipping_parameter',
                    args: {
                        shop_setting: cur_frm.doc.shop_name,
                        order_sn: cur_frm.doc.marketplace_id
                    },callback: function(r) {
                        console.log(r.message.response.pickup.address_list[0].time_slot_list,'rrrrr')
                        let data=[]
                        let tanggal = []
                        let tampil = []
                        let field = [];
                        for(var i=0;i<r.message.response.pickup.address_list[0].time_slot_list.length;i++){
                            data.push(r.message.response.pickup.address_list[0].time_slot_list[i].time_text+"#"+r.message.response.pickup.address_list[0].time_slot_list[i].pickup_time_id)
                            tanggal.push(r.message.response.pickup.address_list[0].time_slot_list[i].date)
                        }
                        let uniq = [...new Set(tanggal)];
                        console.log(uniq,'data')
                        for(var i=0;i<uniq.length;i++){
                            console.log(uniq[i],'ckckc')
                            var date = new Date(0) // mengambil epoch nol (1 jan 1970)
                            date.setUTCSeconds(uniq[i])
                            console.log(date,'i')
                            tampil.push(date+'-'+uniq[i])
                        }
                        field.push(
                        {
                            label: "address_id",
                            fieldname: 'address_id',
                            fieldtype: 'Data',
                            read_only: 1,
                            default: r.message.response.pickup.address_list[0].address_id
                        },
                        {
                            label: "Date",
                            fieldname: 'date',
                            fieldtype: 'Select',
                            options: tampil
                        },
                        {
                            label: "Time",
                            fieldname: 'time',
                            fieldtype: 'Select',
                            options: data
                        }
                        );
                      
       
                        let d = new frappe.ui.Dialog({
                                    title: 'Set Pick Up',
                                    fields: field,
                                    primary_action_label: 'Submit',
                                    primary_action(values) {
                                        console.log(values,"values");
                                        frappe.call({method:'shopee_connector.api.logistic.update_shipping_order',
                                        args: {
                                           shop_name: cur_frm.doc.shop_name,
                                           addres_id: values.address_id,
                                           waktu:values.time,
                                           order_sn: cur_frm.doc.marketplace_id,
                                           tracking_no: cur_frm.doc.tracking_no
                                        },callback: function(r) {

                                        }
                                        });

                                        d.hide();
                                    }

                                });
                                
                        d.show();
                    }                      
            });
    },
    create_shipping_document(frm){
        frappe.msgprint("tes123")
        frappe.confirm(
            'Are you sure to Create Shipping Document ?',
            function(){
                frappe.call({method:'shopee_connector.api.logistic.create_shipping_document',
                    args: {
                        shop_name: cur_frm.doc.shop_name,
                        order_sn: cur_frm.doc.marketplace_id,
                        package_number: cur_frm.doc.tracking_no
                    },callback: function(r) {
                       
                    }                      
                });
            },
            function(){
                show_alert('Thanks for continue here!')
            }
        )
       
    },
	set_pick_up(frm){
		frappe.msgprint('tes')
	    frappe.call({method:'shopee_connector.api.logistic.get_shipping_parameter',
                    args: {
                        shop_setting: cur_frm.doc.shop_name,
                        order_sn: cur_frm.doc.marketplace_id
                    },callback: function(r) {
                        console.log(r.message.response.pickup.address_list[0].time_slot_list,'rrrrr')
                        let data=[]
                        let tanggal = []
                        let tampil = []
                        let field = [];
                       	for(var i=0;i<r.message.response.pickup.address_list[0].time_slot_list.length;i++){
                       		data.push(r.message.response.pickup.address_list[0].time_slot_list[i].time_text+"#"+r.message.response.pickup.address_list[0].time_slot_list[i].pickup_time_id)
                       		tanggal.push(r.message.response.pickup.address_list[0].time_slot_list[i].date)
                       	}
                       	let uniq = [...new Set(tanggal)];
                       	console.log(uniq,'data')
                       	for(var i=0;i<uniq.length;i++){
                       		console.log(uniq[i],'ckckc')
                       		var date = new Date(0) // mengambil epoch nol (1 jan 1970)
							date.setUTCSeconds(uniq[i])
							console.log(date,'i')
							tampil.push(date+'-'+uniq[i])
                       	}
                       	field.push(
                       	{
                            label: "address_id",
                            fieldname: 'address_id',
                            fieldtype: 'Data',
                            read_only: 1,
                            default: r.message.response.pickup.address_list[0].address_id
                        },
                       	{
                            label: "Date",
                            fieldname: 'date',
                            fieldtype: 'Select',
                            options: tampil
                        },
                        {
                            label: "Time",
                            fieldname: 'time',
                            fieldtype: 'Select',
                            options: data
                        }
                        );
                      
       
                        let d = new frappe.ui.Dialog({
                                    title: 'Set Pick Up',
                                    fields: field,
                                    primary_action_label: 'Submit',
                                    primary_action(values) {
                                        console.log(values,"values");
                                        frappe.call({method:'shopee_connector.api.logistic.ship_order',
					                    args: {
					                       shop_name: cur_frm.doc.shop_name,
					                       addres_id: values.address_id,
					                       waktu:values.time,
					                       order_sn: cur_frm.doc.marketplace_id,
                                           tracking_no: cur_frm.doc.tracking_no
					                    },callback: function(r) {

					                    }
					                	});

                                        d.hide();
                                    }

                                });
                                
                        d.show();
                    }                      
            });
	}
})