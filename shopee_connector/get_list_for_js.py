import frappe

@frappe.whitelist()
def get_variation_list_js(name):   
    data = frappe.db.sql(""" SELECT * FROM `tabItem Attribute` WHERE name = '{}' """.format(name),as_list=1)
    data2 = frappe.get_doc("Item Attribute", name)    
    return_value = []
    for i in data2.item_attribute_values:        
        return_value.append(i.attribute_value)
    # frappe.throw(str(return_value))
    # return (listAttribute['attribute_list'])
    return return_value