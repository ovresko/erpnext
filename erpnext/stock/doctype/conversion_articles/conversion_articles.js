// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt



frappe.ui.form.on('Conversion Articles', {
	refresh: function(frm) {

	},
	save: function(frm){
		frappe.call({
                        doc: frm.doc,
                        method: "save_items",
                        callback: function (data) {
                            frappe.show_alert('Done !');
                        }
                    })
	},
	convertir: function(frm){
		
		 //frm.set_value('codes', old); 
		frappe.call({
			method: 'erpnext.stock.doctype.conversion_articles.conversion_articles.get_converstion',
			freeze: true,
			freeze_message: __("Converting..."),
			args: {
				refs: frm.doc.refs,
			},
			callback: function (r) {
				if(r.message){
					frm.set_value('codes', r.message); 				
				}
			}
		});
		
		
	},
	enregistrer: function(frm){
		 
		frappe.call({
			method: 'erpnext.stock.doctype.conversion_articles.conversion_articles.set_address',
			freeze: true,
			args: {
				refs2: frm.doc.refs2,
				stock: frm.doc.stock,
				ads:  frm.doc.ads
			},
			freeze_message: __("Saving..."), 
			callback: function (r) {
				if(r.message){
					frappe.msgprint(r.message) 				
				}
			}
		});
		
		
	}
});
