// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt



frappe.ui.form.on('Conversion Articles', {
	refresh: function(frm) {

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
				frm.reload_doc();
			}
		});
		
		
	}
});
