// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

function open_item_info(item_code) {
			var me  = this;
			
			frappe.call({
					"method": "frappe.client.get",
					"args": {
						"doctype": "Item",
						"name": item_code
					},
					"callback": function(response) {
						var item = response.message; 
						
						if (item) {
							if(me.msg_information)
							{
								//$(me.msg_information).remove();
								me.msg_information = null;
							}
							console.log(item.item_code)
							let image = '';
							let fabricant_logo = '';
							if(item.fabricant_logo){
								fabricant_logo ='<img src="'+item.fabricant_logo+'">';
							}
							if(item.image){
								image ='<img src="'+item.image+'">';
							}
							console.log(image);
							console.log(fabricant_logo);
							me.msg_information = frappe.msgprint(
								`
								<button type="button" data-item-code="${item_code}" class="btn btn-primary btn-sm btn-versions-list" > 
									<span class="hidden-xs">Véhicules Supportées</span>
								</button>
<br>
								<table class="table table-bordered table-condensed">
									<tr><td>${item.item_name}</td><td>
											 ${image} 
										</td></tr>
									<tr> 
										<td>
											<label>${item.item_code}</label>
										</td>
										<td>
											<label>${item.manufacturer_part_no}</label>
										</td>
									</tr> 
								</table>
 
								<table class="table table-bordered table-condensed">
									<tr> 
										<td>
											<label>OEM</label>
										</td>
										<td>
											${item.oem_text}
										</td>
										<td></td>
									</tr>
									<tr> 
										<td>
											<label>Fabricant</label>
										</td>
										<td>
											${item.manufacturer}
										</td>
										<td>
											${fabricant_logo}
										</td>
									</tr>
									<tr> 
										<td>
											<label>Critére</label>
										</td>
										<td>
											${item.critere_text || ''}
										</td>
										<td>
											
										</td>
									</tr>
								</table>
								
								<hr>	
								<label>Complementent </label>
								<div>${item.articles_text || ''}</div>
								<hr>	
								<label>Composants </label>
								<div>${item.composant_text || ''}</div>
								<hr>
 
									
								`,"Détails Article"
								);
								$(me.msg_information.body).find('.btn-versions-list').on('click', () => {
									  
								frappe.call({
									"method": "erpnext.selling.page.point_of_sale.point_of_sale.get_vehicule_details",
									"args": {
										"item_code": item_code
									},
									"callback": function(response) {
										var item = response.message; 
										if (item) {
											
											
											var versions = item[0];
											var generations = item[1];
											var modeles = item[2];
											var marques = item[3];
											
											var html = '';
											html += `<label>Versions: </label><table class="table table-bordered table-condensed">`;
											for (const _v in versions) {
												
												let v = versions[_v];
												 
												html += `<tr>`;
												html += ` 
													<td> ${v.version_vehicule || ''}<br>${v.marque_vehicule || ''} </td>
													 
													<td> ${v.nom_version || ''}  </td>
													<td  style="width:100px"> ${v.periode || ''}</td>
													<td> ${v.critere || ''}  ${v.valeur_1 || ''} <br> ${v.critere_1 || ''}  ${v.valeur_2 || ''} <br> ${v.critere_2 || ''}  ${v.valeur_3 || ''} <br>  </td>
												`;
												html += `</tr>`;
											}
											html += `</table>`;
											
											var html_generations = '';
											html_generations += `<label>Generations: </label><table class="table table-bordered table-condensed">`;
											for (const _v in generations) {
												
												let v = generations[_v];
												 let d = (v.date_debut || '').substring(5,7)+'-'+(v.date_debut || '').substring(2,4)
												 let f = (v.date_fin || '').substring(5,7)+'-'+(v.date_fin || '').substring(2,4)
												html_generations += `<tr>`;
												html_generations += ` 
													<td> ${v.nom_marque || ''} </td>	
													<td> ${v.nom_generation || ''} </td>
													<td style="width:100px"> (${d || ''} ${f || ''}) </td>
													<td> ${v.critere || ''}  ${v.valeur_1 || ''} <br> ${v.critere_1 || ''}  ${v.valeur_2 || ''} <br> ${v.critere_2 || ''}  ${v.valeur_3 || ''} <br>  </td>
												`;
												html_generations += `</tr>`;
											}
											html_generations += `</table>`;
											
											var html_modeles = '';
											html_modeles += `<label>Modeles: </label><table class="table table-bordered table-condensed">`;
											for (const _v in modeles) {
												
												let v = modeles[_v];
												 
												html_modeles += `<tr>`;
												html_modeles += ` 
													<td> ${v.nom_modele || ''} </td>
													<td> ${v.nom_marque || ''} </td>
												`;
												html_modeles += `</tr>`;
											}
											html_modeles += `</table>`;
											
											var html_marques = '';
											html_marques += `<label>Marques: </label><table class="table table-bordered table-condensed">`;
											for (const _v in marques) {
												
												let v = marques[_v];
												 
												html_marques += `<tr>`;
												html_marques += ` 
													<td> ${v.marque || ''} </td>
												`;
												html_marques += `</tr>`;
											}
											html_marques += `</table>`;
											 
											frappe.msgprint(`
												${html}
												${html_generations}
												${html_modeles}
												${html_marques}
											`);
										
										}
										}
								
									});
										 
							});
							console.log(me.msg_information);
							me.msg_information.show();
						}  
					}
				}); 	
	}

function prix_target_item(data) {
	var qty_id = 'prix_target_'+data;
	var qty = $('#'+qty_id).val();
	console.log("prix_target ",qty);
	frappe.call({
			method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.prix_target_item",
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
//qts_target_item
function qts_target_item(data) {
	var qty_id = 'qts_target_'+data;
	var qty = $('#'+qty_id).val();
	frappe.call({
			method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.qts_target_item",
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
//remarque_item
function commentaire_item(data) {
	var qty_id = 'commentaire_'+data;
	var qty = $('#'+qty_id).val();
	frappe.call({
			method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.commentaire_item",
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
//reponse_item
function reponse_item(data) {
	var qty_id = 'reponse_'+data;
	var qty = $('#'+qty_id).val();
	frappe.call({
			method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.reponse_item",
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
//remarque_item
function remarque_item(data) {
	var qty_id = 'remarque_'+data;
	var qty = $('#'+qty_id).val();
	frappe.call({
			method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.remarque_item",
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

function approuver(data){
	frappe.call({
			method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.approuver_item",
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
function en_cours(data){
	frappe.call({
			method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.en_cours_item",
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
function annuler(data){
	frappe.call({
			method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.annuler_item",
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

function negociation(data){
	frappe.call({
			method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.negociation_item",
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

function achat_item(data){
//	
	console.log("code:",data);
	frappe.call({
			method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.set_item_achat",
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
	var qty_id = 'input_'+data;
	var qty = $('#'+qty_id).val();
	frappe.call({
			method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.set_item_demande",
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

frappe.query_reports["Rapport analyse devis fournisseur"] = {
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		
		if (row && row != null && row[2].content!=null && row[2] && row[2].content.length == 11 && row[1].content != null) {
			value = "<div style='color: white;background-color: #008081;padding: 5px;'>" + value + "</div>";
		}
		else if(row && row != null && row[2].content!=null && row[2] && row[2].content.length == 11 && row[1].content == null)
			{
				value = "<div style='color: white;background-color: #802B76;padding: 5px;'>" + value + "</div>";
			}
		else {
			
			
			if(data!= null && data["etat_confirmation"] == "Approuve"){
				value = "<div style='color:green'>" + value + "</div>";
			}else if(data!= null && data["etat_confirmation"] == "Annule"){
				value = "<div style='color:#f5372a;font-weight:bold'>" + value + "</div>";
			}else if(data!= null && data["etat_confirmation"] == "En cours"){
				value = "<div style='color:blue'>" + value + "</div>";
			}else if(data!= null && data["etat_confirmation"] == "En negociation"){
				value = "<div style='color:#E97A13'>" + value + "</div>";
			}else{
				value = "<div style='color:black'>" + value + "</div>";
			}
		}
		return value
	},
	"filters": [
		
		{
			"fieldname": "confirmation",
			"label": "Confirmation",
			"fieldtype": "Select",
			"options": ["","En cours", "Approuve", "Annule","En negociation"],
			"default": ""
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
		},{
			"fieldname": "is_purchase",
			"label": "Article d'achat",
			"fieldtype": "Check",
			"default": 1
		},{
			"fieldname": "is_light",
			"label": "Recherche Rapide",
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
			"default": 1
		},
		{
		"fieldname":"from_date",
		"label": __("From Date"),
		"fieldtype": "Date",
		"default": frappe.datetime.add_days(frappe.datetime.get_today(), -240),
		"width": "80"
	},
	 
	{
		"fieldname": "demande",
		"label": __("Demande de materiel"),
		fieldtype: "Link",
		options: "Material Request", 
		"get_query": function() {
			return {
				"doctype": "Material Request",
				"filters": {
					"status": "Pending",
				}
			}
		}
		
		
	},
	{
		"fieldname": "consultation_interne",
		"label": "Tous Consultation",
		fieldtype: "Link",
		options: "Supplier Quotation", 
		"get_query": function() {
			return {
				"doctype": "Supplier Quotation",
				"filters": {
					"docstatus": 0
				}
			}
		}
	},
	{
		"fieldname": "consultation_externe",
		"label": __("Consultation externe"),
		fieldtype: "Link",
		options: "Supplier Quotation", 
		"get_query": function() {
			return {
				"doctype": "Supplier Quotation",
				"filters": {
					"docstatus": 0,
					//"etat_consultation_deux": "Consultation Externe",
					"etat_mail":"Email Non Envoye",
					"resultat": ["!=", "A Envoyer P1"]
				}
			}
		}
	},
		{
			"fieldname":"paging",
			"label": "Afficher",
			"fieldtype": "Select",
			"options": ["Afficher Tous","Page 1", "Page 2", "Page 3", "Page 4"],
			"default": ""
		},
		{
			"fieldname": "history",
			"label": "Historique",
			"fieldtype": "Check",
			"default": 0
		}
	]
}
