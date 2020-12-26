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
			"fieldname": "cmd",
			"label": "Commande",
			fieldtype: "Link",
			options: "Sales Order",
			"get_query": function() {
				return {
					"doctype": "Sales Order",
					"filters": {
						"workflow_state": "Reservation",
						"docstatus":1
					}
				}
			}
		},
		{
			"fieldname": "disp",
			"label": "Disponible",
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_start_date"),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_end_date"),
		},
	],
	onload: function(report) {
		var me = this;
		frappe.dom.freeze();
		report.page.add_inner_button("Generer Livraison", function() {
			var data = report.data;
			filters = report.get_values()
			items = [];
			customer = filters.customer
			if (customer == null){
				alert("Client invalide");
				return;
			}
			console.log("customer",filters)
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
						 window.open('/printview?doctype=Delivery%20Note&name='+r.message+'&format=Adresses%20Magasin&no_letterhead=0&_lang=fr', '_blank');

						
					}
				}
			});
			//console.log(report);
			
		});
		frappe.dom.unfreeze();
	}
}
