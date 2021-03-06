// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

 

function achat_item(data){
//	
	console.log("code:",data);
	var confirme = confirm("Confirmer l'operation ?");
	if(!confirme){
		return;
	}
	frappe.call({
			method: "erpnext.stock.doctype.item.item.set_item_achat",
			args: {
				item_code: data
			},
			callback: function(r) {
				if (r.message) {
					alert(r.message);
				}
			}
		});
}
function demander_item(data) {
	console.log("code:",data);
	var qty_id = 'input_'+data;
	var qty = $('#'+qty_id).val();
	console.log("qty:",qty);
	var confirme = confirm("Confirmer l'operation ?");
	if(!confirme){
		return;
	}
	frappe.call({
			method: "erpnext.stock.doctype.item.item.set_item_demande",
			args: {
				item_code: data,
				qty: qty
			},
			callback: function(r) {
				if (r.message) {
					alert(r.message);
				}
			}
		});
}

frappe.query_reports["Rapport analyse de besoin"] = {
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
		},{
			"fieldname": "is_purchase",
			"label": "Article d'achat",
			"fieldtype": "Check",
			"default": 1
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
		,{
			"fieldname": "show_price",
			"label": "Afficher les prix",
			"fieldtype": "Check",
			"default": 0
		},
		{
			"fieldname":"entry_status",
			"label": "Etat ",
			"fieldtype": "Select",
			"options": ["","Achetes deja","Non Achetes"],
			"default": ""
		},
		{
			"fieldname":"model_status",
			"label": "Etat par modele",
			"fieldtype": "Select",
			"options": ["","Modele en repture","Repture Article"],
			"default": ""
		}
	]
}
