// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// attach required files
{% include 'erpnext/public/js/controllers/buying.js' %};


frappe.ui.form.on('Supplier Quotation', {
	setup: function(frm) {
		frm.custom_make_buttons = {
			'Purchase Order': 'Purchase Order'
		}
	},
	'download_fiche': function(frm){
		
		if(frm.doc.items != null)
		{
			var data = [];
			var docfields = [];
			//#	Num Consultation	Fabricant	Code Article	Designation	oem	Ref Article	Qts
			//data.push(["Date",frm.doc.transaction_date,"","","","",""]);
			//data.push(["Fournisseur",frm.doc.supplier_name,"","","","",""]);
			data.push(["#" ,"Num Consultation","Fabricant","Code Article","OEM"
				   ,"Designation","Ref Article","Poids","Pays d'origine","Devise","Qts"
				   ,"Prix Offre","Prix Target","Qts Target","Remarque","Prix Final","Qts Final","Confirmation"
				   ,"Commentaire fournisseur","Reponse fournisseur"]);
			
			$.each(frm.doc.items || [], (i, d) => {
				var row = [];
				 	 
					var oem = "";
					if(d["oem"] != null)
					{ 
						oem = d["oem"];
					}
					var fabricant = d["fabricant"];
					var ref_fabricant = d["ref_fabricant"];
					var qty =  Math.floor( d["qty"] * 0.25); 
					var cur = frm.doc.currency;
					var pays ='';
					if(d["pays"] != null && d["pays"] != 'undefined' && d["pays"] != ''){
						pays =d["pays"] ;
					}
					if(qty <= 0){
						qty= 2;
					}
					if(d["qts_original"] == null || d["qts_original"] == 0 )
					{d["qts_original"] = qty;}
					var qts_final = '';
					var offre = '';
					var offre_fournisseur_initial = d["prix_fournisseur"];
					if(d["offre_fournisseur_initial"] != null && d["offre_fournisseur_initial"] > 0)
					{
						offre_fournisseur_initial = d["offre_fournisseur_initial"] 
					}else{
						d["offre_fournisseur_initial"] = d["prix_fournisseur"];
					}
				
				
					if (d["confirmation"] == "Approuve"){
						qts_final = d["qty"];
						offre = d["rate"] ;
					}
					if (d["confirmation"] == "Annule"){
						 
						offre = d["rate"];
					}
					
					var ptarget = '';
					var qtarget = '';
					
					var confirmation = '';
					if (d["confirmation"] != "En negociation"){
						confirmation = d["confirmation"];
					}
					if( d["prix_target"] != null && d["prix_target"]>0)
					{
						ptarget=d["prix_target"] ;
					}
					if( d["qts_target"] != null && d["qts_target"]>0)
					{
						qtarget=d["qts_target"];
					}
					row.push(['"'+i+'"'
						  ,'"'+frm.doc.name+'"'
						  ,'"'+fabricant+'"'
						  ,'"'+d["item_code"]+'"'
						  ,oem
						  ,'"'+d["item_name"]+'"'
						  ,'"'+ref_fabricant+'"'
						  ,'"'+d["weight_per_unit"]+'"'
						  ,'"'+pays+'"' 
						  ,'"'+cur+'"'
						  ,'"'+d["qts_original"]+'"'
						  ,'"'+offre_fournisseur_initial+'"'
						  ,'"'+ptarget+'"'
						  ,'"'+qtarget+'"'
						  ,'"'+d["remarque"]+'"'
						  ,'"'+offre+'"'
						  ,'"'+qts_final+'"'
						  ,confirmation]
						  ,'"'+d["commentaire_fournisseur"]+'"'
						  ,'"'+d["reponse_fournisseur"]+'"');
				 
				data.push(row);
			});

			frappe.tools.downloadify(data, null, "FICHE CONSULTATION "+frm.doc.name+" "+frm.doc.supplier_name);
			frm.save();
		}
	
		
		
		
	},
	'download_fiche_all': function(frm){
		
		if(frm.doc.items != null)
		{
			var data = [];
			var docfields = [];
			//#	Num Consultation	Fabricant	Code Article	Designation	oem	Ref Article	Qts

			//data.push(["Date",frm.doc.transaction_date,"","","","",""]);
			//data.push(["Fournisseur",frm.doc.supplier_name,"","","","",""]);
			data.push(["#" ,"Num Consultation","Fabricant","Code Article","OEM","Designation","Ref Article","Poids","Pays d'origine","Devise","Qts","Prix Offre","Prix Target","Qts Target","Remarque","Offre Final","Prix Final","Qts Final","Confirmation " ,"Commentaire fournisseur","Reponse fournisseur"]);
			
			$.each(frm.doc.items || [], (i, d) => {
				var row = [];
				 	var oem = "";
					if(d["oem"] != null)
					{ 
						oem = d["oem"];
					}
					var fabricant = d["fabricant"];
					var ref_fabricant = d["ref_fabricant"];
					var qty =  Math.floor( d["qty"] * 1); 
					var cur = frm.doc.currency;
				var pays ='';
					if(d["pays"] != null && d["pays"] != 'undefined' && d["pays"] != ''){
						pays =d["pays"] ;
					}
					if(qty <= 0){
						qty= 2;
					}
					if(d["qts_original"] ==null || d["qts_original"] ==0)
					{d["qts_original"] = qty;}
					var qts_final = '';
					var offre = '';
					var offre_fournisseur_initial = d["prix_fournisseur"];
					if(d["offre_fournisseur_initial"] != null && d["offre_fournisseur_initial"] > 0)
					{
						offre_fournisseur_initial = d["offre_fournisseur_initial"] 
					}else{
						d["offre_fournisseur_initial"] = d["prix_fournisseur"];
					}
					if (d["confirmation"] == "Approuve"){
						qts_final = d["qty"];
						offre = d["rate"];
					} 
					if (d["confirmation"] == "Annule"){
						 
						offre = d["rate"];
					}
					var ptarget = '';
					var qtarget = '';
					var confirmation = '';
					if (d["confirmation"] != "En negociation"){
						confirmation = d["confirmation"];
					}
					if( d["prix_target"] != null && d["prix_target"]>0)
					{
						ptarget=d["prix_target"];
					}
					if( d["qts_target"] != null && d["qts_target"]>0)
					{
						qtarget=d["qts_target"];
					}
					row.push(['"'+i+'"'
						  ,'"'+frm.doc.name+'"'
						  ,'"'+fabricant+'"'
						  ,'"'+d["item_code"]+'"'
						  ,oem
						  ,'"'+d["item_name"]+'"'
						  ,'"'+ref_fabricant+'"'
						  ,'"'+d["weight_per_unit"]+'"'
						  ,'"'+pays+'"' 
						  ,'"'+cur+'"'
						  ,'"'+d["qts_original"]+'"'
						  ,'"'+offre_fournisseur_initial+'"'
						  ,'"'+ptarget+'"'
						  ,'"'+qtarget+'"'
						  ,'"'+d["remarque"]+'"'
						  ,'"'+d["prix_fournisseur"]+'"'
						  ,'"'+offre+'"'
						  ,'"'+qts_final+'"'
						  ,confirmation]  
						 ,'"'+d["commentaire_fournisseur"]+'"'
						  ,'"'+d["reponse_fournisseur"]+'"');
				 
				data.push(row);
			});

			frappe.tools.downloadify(data, null, "FICHE CONSULTATION "+frm.doc.name+" "+frm.doc.supplier_name);
			//frm.save();
		}
	
		
		
		
	},
	'importer_articles': function(frm){
	 var me = this;
				if(!frm.doc.__islocal){
					frappe.msgprint("Impossible de charger si document enregistre !");
					return;

				}
				        frappe.dom.freeze();
					cur_frm.clear_table("items"); 
					frappe.call({
					 method: 'erpnext.stock.doctype.material_request.material_request.get_mr_items',
						args:{manufacturer: frm.doc.manufacturer},
					callback: function(r){
						
					cur_frm.clear_table("items"); 
						
							r.message.map(w => {
							console.log("new item : ",w.item_code);
					 var child = cur_frm.add_child("items");
					
					frappe.model.set_value(child.doctype, child.name, "item_code", w.item_code)
					frappe.model.set_value(child.doctype, child.name, "pays", w.pays)
					frappe.model.set_value(child.doctype, child.name, "material_request_item", w.name)
					frappe.model.set_value(child.doctype, child.name, "material_request", w.parent)
					frappe.model.set_value(child.doctype, child.name, "model", w.model)
					frappe.model.set_value(child.doctype, child.name, "consultation", w.consultation)
					frappe.model.set_value(child.doctype, child.name, "consulted", w.consulted)
					frappe.model.set_value(child.doctype, child.name, "item_name", w.item_name)
					frappe.model.set_value(child.doctype, child.name, "qty", w.qty)
					frappe.model.set_value(child.doctype, child.name, "ref_fabricant", w.ref_fabricant)
					frappe.model.set_value(child.doctype, child.name, "fabricant", w.fabricant)
					  
					
						});
						
						console.log("before refresh_field");
						 cur_frm.refresh_field("items"); 
						console.log("after refresh_field");
						if(r.message){ 
							frappe.msgprint("Operation terminee")
							}
					
					}});
					frappe.dom.unfreeze();
	}
	//, 
	//validate: function(frm){
	
		//if(frm.doc.manufacturer){ 
		//var _items = [];	
		//frm.doc.items.forEach(i => {
		//	
		//	if(i.fabricant == frm.doc.manufacturer){
		//		
		//		_items.push(i);
		//	
		//	}
		//
		//});
	
		//frm.doc.items = _items;

		//} 
	
	//}

});

function load_fab(me){
	
 
}
 
 
erpnext.buying.SupplierQuotationController = erpnext.buying.BuyingController.extend({
	refresh: function() {
		var me = this;
		this._super();
		if (this.frm.doc.docstatus === 1) {
			cur_frm.add_custom_button(__("Purchase Order"), this.make_purchase_order,
				__("Make"));
			cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
			cur_frm.add_custom_button(__("Quotation"), this.make_quotation,
				__("Make"));
				
			if(!this.frm.doc.auto_repeat) {	
				cur_frm.add_custom_button(__('Subscription'), function() {
					erpnext.utils.make_subscription(me.frm.doc.doctype, me.frm.doc.name)
				}, __("Make"))
			}
		}
		else if (this.frm.doc.docstatus===0) {

			this.frm.add_custom_button(__('Material Request'),
				function() {
					
					frappe.call({
					 method: 'erpnext.stock.doctype.material_request.material_request.get_supplier_quotation',
					args:{manufacturer: me.frm.doc.manufacturer},
					callback: function(r){
						let res = [];
						r.message.map(w => {
							res.push(w.name);
						})
						console.log("from cust");
						if(res){					
					erpnext.utils.map_current_doc({
						method: "erpnext.stock.doctype.material_request.material_request.make_supplier_quotation",
						source_doctype: "Material Request",
						predef: res,
						target: me.frm,
						setters: {
							company: me.frm.doc.company
						},
						get_query_filters: {
							material_request_type: "Purchase",
							docstatus: 1,
							status: ["!=", "Stopped"],
							per_ordered: ["<", 99.99]
						}
					});
								
						}}});	
				}, __("Get items from"));
		}
	},

	make_purchase_order: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.make_purchase_order",
			frm: cur_frm
		})
	},
	make_quotation: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.make_quotation",
			frm: cur_frm
		})

	}
});

 

// for backward compatibility: combine new and previous states
$.extend(cur_frm.cscript, new erpnext.buying.SupplierQuotationController({frm: cur_frm}));

cur_frm.fields_dict['items'].grid.get_field('project').get_query =
	function(doc, cdt, cdn) {
		return{
			filters:[
				['Project', 'status', 'not in', 'Completed, Cancelled']
			]
		}
	}
