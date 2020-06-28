// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.utils");

erpnext.utils.open_msg = function(msg) {
	frappe.msgprint(msg);
}

erpnext.utils.open_item_info =  function(item_code,me) {
	var me = me;
	console.log("open_item_info");
	frappe.call({
			"method": "frappe.client.get",
			"args": {
				"doctype": "Item",
				"name": item_code
			},
			"callback": function(response) {
				var item = response.message; 
				 
				if (item) {
					//console.log("item",item);
					// if(me.msg_information)
					// {
					//	 me.msg_information.hide(); 
					 //}
					erpnext.utils.open_msg("test);
					let image = '';
					let fabricant_logo = '';
					if(item.fabricant_logo){
						fabricant_logo ='<img src="'+item.fabricant_logo+'">';
					}
					if(item.image){
						image ='<img src="'+item.image+'">';
					}

					//me.msg_information = 
						//frappe.msgprint(
					
					var _modal =
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
  			 
                        `;
					 let msg_information = frappe.msgprint(_modal,"Details Article");
					 //msg_information.hide();
					//msg_information.show();
                       			// $(_modal).modal();
					//$(me.msg_information.body).find('.btn-versions-list').on('click', () => {
					
					$('.btn-versions-list').on('click', () => {
						console.log("click");
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
					 
					// msg_information.show();
				}  
			}
		}); 	
}
erpnext.utils.get_party_details = function(frm, method, args, callback) {
	if(!method) {
		method = "erpnext.accounts.party.get_party_details";
	}
	if(!args) {
		if((frm.doctype != "Purchase Order" && frm.doc.customer)
			|| (frm.doc.party_name && in_list(['Quotation', 'Opportunity'], frm.doc.doctype))) {

			let party_type = "Customer";
			if(frm.doc.quotation_to && frm.doc.quotation_to === "Lead") {
				party_type = "Lead";
			}

			args = {
				party: frm.doc.customer || frm.doc.party_name,
				party_type: party_type,
				price_list: frm.doc.selling_price_list
			};
		} else if(frm.doc.supplier) {
			args = {
				party: frm.doc.supplier,
				party_type: "Supplier",
				bill_date: frm.doc.bill_date,
				price_list: frm.doc.buying_price_list
			};
		}

		if (args) {
			args.posting_date = frm.doc.posting_date || frm.doc.transaction_date;
		}
	}
	if(!args || !args.party) return;

	if(frappe.meta.get_docfield(frm.doc.doctype, "taxes")) {
		if(!erpnext.utils.validate_mandatory(frm, "Posting/Transaction Date",
			args.posting_date, args.party_type=="Customer" ? "customer": "supplier")) return;
	}

	args.currency = frm.doc.currency;
	args.company = frm.doc.company;
	args.doctype = frm.doc.doctype;
	frappe.call({
		method: method,
		args: args,
		callback: function(r) {
			if(r.message) {
				frm.supplier_tds = r.message.supplier_tds;
				frm.updating_party_details = true;
				frappe.run_serially([
					() => frm.set_value(r.message),
					() => {
						frm.updating_party_details = false;
						if(callback) callback();
						frm.refresh();
						erpnext.utils.add_item(frm);
					}
				]);
			}
		}
	});
}

erpnext.utils.add_item = function(frm) {
	if(frm.is_new()) {
		var prev_route = frappe.get_prev_route();
		if(prev_route[1]==='Item' && !(frm.doc.items && frm.doc.items.length)) {
			// add row
			var item = frm.add_child('items');
			frm.refresh_field('items');

			// set item
			frappe.model.set_value(item.doctype, item.name, 'item_code', prev_route[2]);
		}
	}
}

erpnext.utils.get_address_display = function(frm, address_field, display_field, is_your_company_address) {
	if(frm.updating_party_details) return;

	if(!address_field) {
		if(frm.doctype != "Purchase Order" && frm.doc.customer) {
			address_field = "customer_address";
		} else if(frm.doc.supplier) {
			address_field = "supplier_address";
		} else return;
	}

	if(!display_field) display_field = "address_display";
	if(frm.doc[address_field]) {
		frappe.call({
			method: "frappe.contacts.doctype.address.address.get_address_display",
			args: {"address_dict": frm.doc[address_field] },
			callback: function(r) {
				if(r.message) {
					frm.set_value(display_field, r.message)
				}
				erpnext.utils.set_taxes(frm, address_field, display_field, is_your_company_address);
			}
		})
	} else {
		frm.set_value(display_field, '');
	}
};

erpnext.utils.set_taxes = function(frm, address_field, display_field, is_your_company_address) {
	if(frappe.meta.get_docfield(frm.doc.doctype, "taxes") && !is_your_company_address) {
		if(!erpnext.utils.validate_mandatory(frm, "Lead/Customer/Supplier",
			frm.doc.customer || frm.doc.supplier || frm.doc.lead || frm.doc.party_name , address_field)) {
			return;
		}

		if(!erpnext.utils.validate_mandatory(frm, "Posting/Transaction Date",
			frm.doc.posting_date || frm.doc.transaction_date, address_field)) {
			return;
		}
	} else {
		return;
	}

	var party_type, party;
	if (frm.doc.lead) {
		party_type = 'Lead';
		party = frm.doc.lead;
	} else if (frm.doc.customer) {
		party_type = 'Customer';
		party = frm.doc.customer;
	} else if (frm.doc.supplier) {
		party_type = 'Supplier';
		party = frm.doc.supplier;
	} else if (frm.doc.quotation_to){
		party_type = frm.doc.quotation_to;
		party = frm.doc.party_name;
	}

	frappe.call({
		method: "erpnext.accounts.party.set_taxes",
		args: {
			"party": party,
			"party_type": party_type,
			"posting_date": frm.doc.posting_date || frm.doc.transaction_date,
			"company": frm.doc.company,
			"billing_address": ((frm.doc.customer || frm.doc.lead) ? (frm.doc.customer_address) : (frm.doc.supplier_address)),
			"shipping_address": frm.doc.shipping_address_name
		},
		callback: function(r) {
			if(r.message){
				frm.set_value("taxes_and_charges", r.message)
			}
		}
	});
}

erpnext.utils.get_contact_details = function(frm) {
	if(frm.updating_party_details) return;

	if(frm.doc["contact_person"]) {
		frappe.call({
			method: "frappe.contacts.doctype.contact.contact.get_contact_details",
			args: {contact: frm.doc.contact_person },
			callback: function(r) {
				if(r.message)
					frm.set_value(r.message);
			}
		})
	}
}

erpnext.utils.validate_mandatory = function(frm, label, value, trigger_on) {
	if(!value) {
		frm.doc[trigger_on] = "";
		refresh_field(trigger_on);
		frappe.msgprint(__("Please enter {0} first", [label]));
		return false;
	}
	return true;
}

erpnext.utils.get_shipping_address = function(frm, callback){
	if (frm.doc.company) {
		frappe.call({
			method: "frappe.contacts.doctype.address.address.get_shipping_address",
			args: {
				company: frm.doc.company,
				address: frm.doc.shipping_address
			},
			callback: function(r){
				if(r.message){
					frm.set_value("shipping_address", r.message[0]) //Address title or name
					frm.set_value("shipping_address_display", r.message[1]) //Address to be displayed on the page
				}

				if(callback){
					return callback();
				}
			}
		});
	} else {
		frappe.msgprint(__("Select company first"));
	}
}
