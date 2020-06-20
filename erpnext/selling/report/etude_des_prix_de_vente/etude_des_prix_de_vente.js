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
								//me.msg_information.hide();
								//me.msg_information = null;
							}
							 
							let image = '';
							let fabricant_logo = '';
							if(item.fabricant_logo){
								fabricant_logo ='<img src="'+item.fabricant_logo+'">';
							}
							if(item.image){
								image ='<img src="'+item.image+'">';
							}
							 
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
							 
							me.msg_information.show();
						}  
					}
				}); 	
	}


function set_price_item(pl,item) {
	  
	var val_id = 'price_'+item+'_'+pl.replace(/ /g,'');
 
	 
	var val = $('#'+val_id).val();
	
     	var qts_id = 'qts_'+item+'_'+pl.replace(/ /g,'');
	var qts = $('#'+qts_id).val();

 	var btn_id = 'btn_'+item+'_'+pl.replace(/ /g,'');
	  
	frappe.call({
		method: "erpnext.stock.doctype.price_list.price_list.update_price",
		args: {
			item_code: item,
			price_list:pl,
			_price: val,
			qts:qts
		},
		callback: function(r) {
			if (r.message) {
				alert(r.message);
				$('#'+btn_id).css('color', 'green');
				$('.prix_traite_text_'+item).text("En cours");
			}
		}
	});
	
}


frappe.query_reports["Etude des prix de vente"] = {
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		
		if (data!=null && data["item_code"] &&  data["item_code"].length == 11 ) {
			value = "<div style='color: white;background-color: #008081;padding: 5px;'>" + value + "</div>";
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
			"default": 1
		}
	],
	onload: function(report) {
		var me = this;
		report.page.add_inner_button("Convertir En Cours", function() {
			var data = report.data;
			data.forEach( (item) => {
				var item_code = item['item_code'];
				console.log(item_code);
				me.switch_etat(item_code,"Approuve");
			});
			//console.log(report);
			
		});
	}
}
