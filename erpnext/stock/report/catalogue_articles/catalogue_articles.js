// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Catalogue Articles"] = {
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		var ovalue = value;
		
		 if(data != null && data != undefined){			
			 
			 if(data["item_code"] && data["item_code"].length == 14)
			 {
				 value = "<div style='color: white;background-color: #ca4100;padding: 1px;'>" + ovalue + "</div>";
			 }
			  if(data["item_code"] &&  (data["item_code"].length == 11 || data["item_code"].includes("----")) )
			 {
				 value = "<div style='color: white;background-color: #383484;padding: 1px;'>" + ovalue + "</div>";
			 }
		 }
		
		
		
		
		//else {
		//	value = "<div style='color:black'>" + value + "</div>";
		//}
		return value
	},
	"filters": [
		{
			"fieldname": "item_code",
			"label": "Code d'article",
			fieldtype: "Data"
		},
		{
			"fieldname": "ref_fabricant",
			"label": "Ref Fabricant",
			fieldtype: "Data"
		},
		{
			"fieldname": "group",
			"label": __("Item Group"),
			fieldtype: "Link",
			options: "Item Group"
		},{
			"fieldname": "variant_of",
			"label": "Modéle",
			fieldtype: "Link",
			options: "Item",
			"get_query": function() {
			return {
				"doctype": "Item",
				"filters": {
					"has_variants": 1,
					   }
				}
			}
		},
		{
			"fieldname": "marque_v",
			"label": __("Marque vehicule"),
			fieldtype: "Link",
			options: "Marque vehicule"
		},
		{
			"fieldname": "modele_v",
			"label": __("Modele vehicule"),
			fieldtype: "Link",
			options: "Modele de vehicule"
		},
		{
			"fieldname": "generation_v",
			"label": "Generation vehicule",
			fieldtype: "Link",
			options: "Generation vehicule"
		}, 
		{
			"fieldname": "version",
			"label": __("Version vehicule"),
			fieldtype: "Link",
			options: "Version vehicule"
		},
		
		
		{
			"fieldname":"manufacturer",
			"label": __("Manufacturer"),
			"fieldtype": "MultiSelect",
			get_data: function() {
				var manufacturers = frappe.query_report.get_filter_value("manufacturer") || "";

				const values = manufacturers.split(/\s*,\s*/).filter(d => d);
				const txt = manufacturers.match(/[^,\s*]*$/)[0] || '';
				let data = [];

				frappe.call({
					type: "GET",
					method:'frappe.desk.search.search_link',
					async: false,
					no_spinner: true,
					args: {
						doctype: "Manufacturer",
						txt: txt,
						filters: {
							"name": ["not in", values]
						}
					},
					callback: function(r) {
						data = r.results;
					}
				});
				return data;
			} 
		},
		{
			"fieldname":"age_plus",
			"label": __("Age plus que"),
			"fieldtype": "Select",
			"options": ["","1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"],
			"default": ""
		},
		{
			"fieldname":"age_minus",
			"label": __("Age moin que"),
			"fieldtype": "Select",
			"options": ["","1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"],
			"default": ""
		},
		{
			"fieldname": "perfection",
			"label": "Perfection",
			fieldtype: "Link",
			options: "Perfection"
			
		},
		{
			"fieldname": "price_list",
			"label": "Liste de prix",
			"fieldtype": "MultiSelect",
			get_data: function() {
				var pl = frappe.query_report.get_filter_value("price_list") || "";
				//Price List

				const values = pl.split(/\s*,\s*/).filter(d => d);
				const txt = pl.match(/[^,\s*]*$/)[0] || '';
				let data = [];

				frappe.call({
					type: "GET",
					method:'frappe.desk.search.search_link',
					async: false,
					no_spinner: true,
					args: {
						doctype: "Price List",
						txt: txt,
						filters: {
							"name": ["not in", values],
							"selling": 1,
							"buying": 0
						}
					},
					callback: function(r) {
						data = r.results;
					}
				});
				return data;
			} 
			
		},
		{
			"fieldname": "recu",
			"label": __("Purchase Receipt"),
			fieldtype: "Link",
			options: "Purchase Receipt"			
		},
		{
			"fieldname":"manufacturer_lp",
			"label": "Fabricant LP",
			"fieldtype": "MultiSelect",
			get_data: function() {
				var manufacturers = frappe.query_report.get_filter_value("manufacturer_lp") || "";

				const values = manufacturers.split(/\s*,\s*/).filter(d => d);
				const txt = manufacturers.match(/[^,\s*]*$/)[0] || '';
				let data = [];

				frappe.call({
					type: "GET",
					method:'frappe.desk.search.search_link',
					async: false,
					no_spinner: true,
					args: {
						doctype: "Manufacturer",
						txt: txt,
						filters: {
							"name": ["not in", values]
						}
					},
					callback: function(r) {
						data = r.results;
					}
				});
				return data;
			} 
		},
		{
			"fieldname": "depot_qty",
			"label": "Disponible Depot",
			"fieldtype": "Check",
			"default": 0
		},
		{
			"fieldname": "magasin_qty",
			"label": "Disponible Magasin",
			"fieldtype": "Check",
			"default": 0
		},
		{
			"fieldname": "has_price",
			"label": "Articles Avec Prix Seulement",
			"fieldtype": "Check",
			"default": 0
		},
		{
			"fieldname": "only_fabricant",
			"label": "Fabricant selec. seul.",
			"fieldtype": "Check",
			"default": 0
		},
		{
			"fieldname": "regroupe",
			"label": "Regroupe",
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname": "hide_prices",
			"label": "Cacher les prix",
			"fieldtype": "Check",
			"default": 0
		},
		{
			"fieldname": "hide_qty",
			"label": "Cacher les qts",
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname": "generate_pdf",
			"label": "Exporter catalogue",
			"fieldtype": "Check",
			"default": 0
		}

	],
	onload: function(report) {
		var me = this;
		report.page.add_inner_button("Exporter Catalogue PDF", function() {
			var data = report.data;
			var items = [];
			data.forEach( (item) => {
				var item_code = item['item_code'];
				if(item_code && item_code!="Total" && !item_code.includes("----") ){
					items.push(item_code);
				}
				
			});
			
			$.get( "/api/method/erpnext.stock.doctype.item.item.bulk_print_list",{"names":encodeURIComponent(items)});

			
			
			
		});
	}
}
