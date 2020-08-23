// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

function switch_etat(item_code,etat) {
	etat = $('.prix_traite_text_'+item_code).first().text();
	console.log("etat",etat);
	frappe.call({
		method: "erpnext.stock.doctype.price_list.price_list.switch_etat",
		args: {
			item_code: item_code,
			etat:etat
		},
		callback: function(r) {
			if (r.message) {
				console.log("setting ",etat);
				$('.prix_traite_btn_'+item_code).text(etat);
				$('.prix_traite_text_'+item_code).text(r.message);
				alert(r.message);				
			}
		}
	});
}
 
function set_price_item(pl,item,valuation) {
	  
	var val_id = 'price_'+item+'_'+pl.replace(/ /g,'');
 
	 
	var val = $('#'+val_id).val();
	
     	var qts_id = 'qts_'+item+'_'+pl.replace(/ /g,'');
	var qts = $('#'+qts_id).val();

 	var btn_id = 'btn_'+item+'_'+pl.replace(/ /g,'');
	var price_id = 'price_'+item+'_'+pl.replace(/ /g,'');
	  
	frappe.call({
		method: "erpnext.stock.doctype.price_list.price_list.update_price",
		args: {
			item_code: item,
			price_list:pl,
			_price: val,
			qts:qts,
			valuation : valuation
		},
		callback: function(r) {
			if (r.message) {
				alert(r.message);
				$('#'+price_id).css('background', '#81ff81');
				$('.prix_traite_text_'+item).text("En cours");
			}
		}
	});
	
}


frappe.query_reports["Etude des prix de vente"] = {
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		var ovalue = value;
		 if(data != null && data != undefined){
			 
			 
			if (data!=null && data['prix_traite'].includes("Approuve")) {
				value = "<div style='color:#008000;padding: 0px;'>" + ovalue + "</div>";
			}
			if (data!=null && data['prix_traite'].includes("En cours")) {
				value = "<div style='color: #FC4136;padding: 0px;'>" + ovalue + "</div>";
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
		},
		{
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
			"fieldname": "price_list",
			"label": "Liste de prix",
			fieldtype: "Link",
			options: "Price List"
		},
		{
		"fieldname": "receipt",
		"label": "Recu d'achat",
		fieldtype: "Link",
		options: "Purchase Receipt", 
			"get_query": function() {
				return {
					"doctype": "Purchase Receipt",
					"filters": {
						"docstatus": "1",
					}
				}
			}
		},
		{
			"fieldname":"prix_traite",
			"label": "Etat Etude",
			"fieldtype": "Select",
			"options": ["","Approuve","En cours"],
			"default": ""
		},
		{
			"fieldname": "with_qty",
			"label": "Avec Qts",
			"fieldtype": "Check",
			"default": 0
		}
	],
	onload: function(report) {
		var me = this;
		report.page.add_inner_button("Convertir Tous En Cours", function() {
			var data = report.data;
			items = [];
			data.forEach( (item) => {
				var item_code = item['item_code'];
				if(item_code && item_code!="Total"){
					items.push(item_code);
					 
				}
				
			});
			console.log(items);
			frappe.call({
				method: "erpnext.stock.doctype.price_list.price_list.switch_etat_bulk",
				args: {
					items: items,
				},
				callback: function(r) {
					if (r.message) {
						
						alert(r.message);				
					}
				}
			});
			//console.log(report);
			
		});
	}
}
