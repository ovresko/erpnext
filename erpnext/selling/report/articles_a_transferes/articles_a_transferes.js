// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Articles a transferes"] = {
	"filters": [
		{
			"fieldname": "warehouse",
			"label": "Stock Cible",
			fieldtype: "Link",
			options: "Warehouse"
		},
		{
			"fieldname": "source_warehouse",
			"label": "Stock Source",
			fieldtype: "Link",
			options: "Warehouse"
		}
		,{
			"fieldname": "grouped",
			"label": "Grouper les qts",
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname": "disp",
			"label": "Disponible seulement",
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname": "ntraite",
			"label": "Non traites seulement",
			"fieldtype": "Check",
			"default": 1
		},{
			"fieldname": "cmd",
			"label": "Commandes",
			"fieldtype": "Check",
			"default": 0
		}
	],
	onload: function(report) {
		var me = this;
		frappe.dom.freeze();
		report.page.add_inner_button("Generer transfert", function() {
			var data = report.data;
			items = [];
			data.forEach( (item) => {
				var item_code = item['item'];
				if(item_code && item_code!="Total"){
					items.push(item);					 
				}
				
			});
			//console.log(items);
			frappe.call({
				method: "erpnext.selling.page.point_of_sale.point_of_sale.get_transfer",
				freeze: true,
				args: {
					items: items,
				},
				callback: function(r) {
					if (r.message) {
							
						frappe.call({
								method: "erpnext.selling.page.point_of_sale.point_of_sale.finish_transfer",
								freeze: true,
								args: {
									items: items,
								},
								callback: function(r) {
									if (r.message) {						
										 alert("Demandes articles fermees");
									}
								}
							});
						 window.open('/desk#Form/Stock%20Entry/'+r.message, '_blank');
					}
				}
			});
			//console.log(report);
			
		});
		frappe.dom.unfreeze();
	}
}
