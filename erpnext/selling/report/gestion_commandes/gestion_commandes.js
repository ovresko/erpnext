// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Gestion Commandes"] = {
	"filters": [
		{
			"fieldname": "customer",
			"label": "Client",
			fieldtype: "Link",
			options: "Customer"
		},
		{
			"fieldname": "disp",
			"label": "Disponible",
			"fieldtype": "Check",
			"default": 1
		}
	],
	onload: function(report) {
		var me = this;
		frappe.dom.freeze();
		report.page.add_inner_button("Generer Livraison", function() {
			var data = report.data;
			items = [];
			customer = report.filters.customer
			data.forEach( (item) => {
				var item_code = item['item'];
				if(item_code && item_code!="Total" && item_code!="_"){
					items.push(item);					 
				}
				
			});
			//console.log(items);
			frappe.call({
				method: "erpnext.selling.page.point_of_sale.point_of_sale.get_delivery",
				freeze: true,
				args: {
					items: items,
					customer: customer
				},
				callback: function(r) {
					if (r.message) {
						 window.open('/desk#Form/Delivery%20Note/'+r.message, '_blank');
					}
				}
			});
			//console.log(report);
			
		});
		frappe.dom.unfreeze();
	}
}
