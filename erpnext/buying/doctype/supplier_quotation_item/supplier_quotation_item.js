// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Supplier Quotation Item', {
	refresh: function(frm) {
		frm.set_value("red_devis",frm.doc.parent);
	}
});
