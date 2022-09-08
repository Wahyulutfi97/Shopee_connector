// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Shopee', {
	refresh(frm) {
		// your code here
	},
	onload(frm) {
		frm.set_query("child_1", function () {
			return {
				"filters": {
					"parent_category_id": ["=", frm.doc.category_parent]
				}
			};
		});

		frm.set_query("child_2", function () {
			return {
				"filters": {
					"parent_category_id": ["=", frm.doc.child_1]
				}
			};
		});

		frm.set_query("child_3", function () {
			return {
				"filters": {
					"parent_category_id": ["=", frm.doc.child_2]
				}
			};
		});

		frm.set_query("child_4", function () {
			return {
				"filters": {
					"parent_category_id": ["=", frm.doc.child_3]
				}
			};
		});

		frm.set_query("id_brand", function () {
			var temp = frm.doc.child_4 ? frm.doc.child_4 : (frm.doc.child_3 ? frm.doc.child_3 : (frm.doc.child_2 ? frm.doc.child_2 : frm.doc.child_1));
			var fillter = '%' + temp + '%';
			return {
				"filters": {
					"use_in_category_id": ["like", fillter]
				}
			};
		});
	},
	get_specifications(frm) {
		var temp = frm.doc.child_4 ? frm.doc.child_4 : (frm.doc.child_3 ? frm.doc.child_3 : (frm.doc.child_2 ? frm.doc.child_2 : frm.doc.child_1));
		frappe.call({
			method: "shopee_connector.api.attribute.get_attribute_list_js",
			args: {
				'shopee_setting': frm.doc.shopee_setting,
				'category_id': temp
			},
			callback: function (r) {
				if (r.message) {
					cur_frm.clear_table("specifications");
					for (let i = 0; i < r.message.length; i++) {
						var childTable = cur_frm.add_child("specifications");
						childTable.attribute_id = r.message[i].attribute_id;
						childTable.display_name = r.message[i].display_attribute_name;
						childTable.input_type = r.message[i].input_type;
						childTable.is_mandatory = String(r.message[i].is_mandatory);
						childTable.attribute_unit = r.message[i].attribute_unit[0]; //Ex : category_id:101955(RAM) , attribute_id:100461, harus ada attribute_unit, yg isinya 'attribute_unit': ['GB']

						if (r.message[i].input_type == "DROP_DOWN") {
							// console.log('Input Drop Down');
							let arrayOption = [];
							for (let x = 0; x < r.message[i].attribute_value_list.length; x++) {
								console.log('Loop select');
								var optionId = r.message[i].attribute_value_list[x].value_id;
								var optionDisplay = r.message[i].attribute_value_list[x].display_value_name;
								var option = "".concat(optionDisplay, ' # ', optionId);
								arrayOption.push(option);
							}
							// console.log(arrayOption);
							var df = frappe.meta.get_docfield("Attribute Shopee", "drop_down", cur_frm.doc.specifications[i]['parent']);
							df.options = arrayOption;
							// console.log(df);
							// childTable.set_df_property( 'drop_down', 'options', arrayOption );
							cur_frm.refresh_fields('specifications');
						}

						if (r.message[i].input_type == "MULTIPLE_SELECT_COMBO_BOX") {
							let arrayOption = [];
							for (let x = 0; x < r.message[i].attribute_value_list.length; x++) {
								var optionId = r.message[i].attribute_value_list[x].value_id;
								var optionDisplay = r.message[i].attribute_value_list[x].display_value_name;
								var option = "".concat(optionDisplay, ' # ', optionId);
								arrayOption.push(option);
							}
							console.log(arrayOption);
							var df = frappe.meta.get_docfield("Attribute Shopee", "multiple_select_combo_box", cur_frm.doc.specifications[i]['parent']);
							df.options = arrayOption;
							// console.log(df);
							// childTable.set_df_property( 'drop_down', 'options', arrayOption );
							cur_frm.refresh_fields('specifications');
						}

						if (r.message[i].input_type == "COMBO_BOX") {
							let arrayOption = [];
							for (let x = 0; x < r.message[i].attribute_value_list.length; x++) {
								var optionId = r.message[i].attribute_value_list[x].value_id;
								var optionDisplay = r.message[i].attribute_value_list[x].display_value_name;
								var option = "".concat(optionDisplay, ' # ', optionId);
								arrayOption.push(option);
							}
							// console.log(arrayOption);
							var df = frappe.meta.get_docfield("Attribute Shopee", "combo_box", cur_frm.doc.specifications[i]['parent']);
							df.options = arrayOption;
							// console.log(df);
							// childTable.set_df_property( 'drop_down', 'options', arrayOption );
							cur_frm.refresh_fields('specifications');
						}
					}
					cur_frm.refresh_fields("specifications");
				}
			}
		});
	},
	name_variation_1(frm) {
		frappe.call({
			method: "shopee_connector.get_list_for_js.get_variation_list_js",
			args: {
				'name': frm.doc.name_variation_1
			},
			callback: function (r) {
				if (r.message) {
					cur_frm.clear_table("variation_1");
					for (let i = 0; i < r.message.length; i++) {
						console.log(r.message[i]);
						var childTable = cur_frm.add_child("variation_1");
						childTable.option = r.message[i];
					}
					cur_frm.refresh_fields("variation_1");
				}
			}
		});
	},
	name_variation_2(frm) {
		frappe.call({
			method: "shopee_connector.get_list_for_js.get_variation_list_js",
			args: {
				'name': frm.doc.name_variation_2
			},
			callback: function (r) {
				if (r.message) {
					cur_frm.clear_table("variation_2");
					for (let i = 0; i < r.message.length; i++) {
						console.log(r.message[i]);
						var childTable = cur_frm.add_child("variation_2");
						childTable.option = r.message[i];
					}
					cur_frm.refresh_fields("variation_2");
				}
			}
		});
	}
})

frappe.ui.form.on('Attribute Shopee', {
	text_filed(frm, cdt, cdn) {
		// frappe.model.set_value('Attribute Shopee', cdn, 'output', d.text_filed);
		$.each(frm.doc.specifications, function (i, d) {
			if (d.input_type == "TEXT_FILED") {
				frappe.model.set_value(d.doctype, d.name, 'output', d.text_filed);
			}
		});
		frm.refresh();
	},
	drop_down(frm, cdt, cdn) {
		$.each(frm.doc.specifications, function (i, d) {
			if (d.input_type == "DROP_DOWN") {
				frappe.model.set_value(d.doctype, d.name, 'output', d.drop_down);
				frappe.model.set_value(d.doctype, d.name, 'value_id', String(d.drop_down).split(" # ")[1]);
			}
		});
		frm.refresh();
	},
	combo_box(frm, cdt, cdn) {
		$.each(frm.doc.specifications, function (i, d) {
			if (d.input_type == "COMBO_BOX") {
				frappe.model.set_value(d.doctype, d.name, 'output', d.combo_box);
				frappe.model.set_value(d.doctype, d.name, 'value_id', String(d.combo_box).split(" # ")[1]);
			}
		});
		frm.refresh();
	},
	multiple_select_combo_box(frm, cdt, cdn) {
		$.each(frm.doc.specifications, function (i, d) {
			if (d.input_type == "MULTIPLE_SELECT_COMBO_BOX") {
				frappe.model.set_value(d.doctype, d.name, 'output', d.multiple_select_combo_box);
				frappe.model.set_value(d.doctype, d.name, 'value_id', String(d.multiple_select_combo_box).split(" # ")[1]);
			}
		});
		frm.refresh();
	},
});

