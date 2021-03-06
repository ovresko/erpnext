// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */



function demander_item(data) {
	console.log("code:",data);
	var qty_id = 'input_'+data;
	var qty = $('#'+qty_id).val();
	console.log("qty:",qty);
	var warehouse = $("input[data-fieldname='warehouse']").val();
	console.log("warehouse:",warehouse);
	if(!warehouse)
	{
		alert("Entrepot invalide");
	}
	var confirme = confirm("Confirmer l'operation ?");
	if(!confirme){
		return;
	}
	frappe.call({
			method: "erpnext.stock.doctype.item.item.set_item_transfer",
			args: {
				item_code: data,
				qty: qty,
				warehouse: warehouse
			},
			callback: function(r) {
				if (r.message) {
					alert(r.message);
				}
			}
		});
}

frappe.query_reports["Rapport analyse depot"] = {
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		var ovalue = value;
		
		 if(data != null && data != undefined){
			 if(data["qts_demande"] > 0){
			value = "<div style='color: #2E7FF8;padding: 1px;'>" + ovalue + "</div>";
			}
			if(data["qts_consulte"] > 0){
				value = "<div style='color: #D75F00;padding: 1px;'>" + ovalue + "</div>";
			}
			if(data["qts_comm"] +data["qts_non_recue"] + data["qts"] > 0){
				value = "<div style='color: #11AF22;padding: 1px;'>" + ovalue + "</div>";
			}
			 
			 if(data["item_code"].length == 14)
			 {
				 value = "<div style='color: white;background-color: #ca4100;padding: 1px;'>" + ovalue + "</div>";
			 }
			  if(data["item_code"].length == 11)
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
			"fieldname": "warehouse",
			"label": "Stock Cible",
			fieldtype: "Link",
			options: "Warehouse"
		},
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
			fieldtype: "Link",
			options: "Price List"
			
		},
		{
			"fieldname": "recu",
			"label": __("Purchase Receipt"),
			fieldtype: "Link",
			options: "Purchase Receipt"			
		}
		,{
			"fieldname": "grouped",
			"label": "Grouper par modele",
			"fieldtype": "Check",
			"default": 0
		},
		{
			"fieldname":"qts_min",
			"label":"Qts minimum",
			"fieldtype": "Int",
			"default": ""
		},
		{
			"fieldname": "disp_g",
			"label": "Disponible depot",
			"fieldtype": "Check",
			"default": 0
		},
		{
			"fieldname": "demande",
			"label": "Inclus La qts demandee",
			"fieldtype": "Check",
			"default": 1
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
		}
	]
}
