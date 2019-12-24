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

			data.push(["Date",frm.doc.transaction_date,"","","","",""]);
			data.push(["Fournisseur",frm.doc.supplier_name,"","","","",""]);
			data.push(["#","Num Consultation","Fabricant","Code Article","Designation","Ref Article","Qts"]);
			$.each(frm.doc.items || [], (i, d) => {
				var row = [];
				 
					var fabricant = d["fabricant"];
					var ref_fabricant = d["ref_fabricant"];
					var qty =  Math.floor( d["qty"] * 0.7);
					  

					row.push([""+i,frm.doc.name,fabricant,d["item_code"],d["item_name"],ref_fabricant,qty] || [""]);
				 
				data.push(row);
			});

			frappe.tools.downloadify(data, null, "FICHE CONSULTATION "+frm.doc.supplier_name);
		}
	
		
		
		
	},
	'download_fiche_all': function(frm){
		
		if(frm.doc.items != null)
		{
			var data = [];
			var docfields = [];
			data.push(["Date",frm.doc.transaction_date,"","","","",""]);
			data.push(["Fournisseur",frm.doc.supplier_name,"","","","",""]);
			data.push(["#","Num Consultation","Fabricant","Code Article","Designation","Ref Article","Qts"]);
			$.each(frm.doc.items || [], (i, d) => {
				var row = [];
				 
					var fabricant = d["fabricant"];
					var ref_fabricant = d["ref_fabricant"];
					var qty =  Math.floor( d["qty"] * 0.7);
					  

					row.push([""+i,frm.doc.name,fabricant,d["item_code"],d["item_name"],ref_fabricant,qty] || [""]);
				 
				data.push(row);
			});

			frappe.tools.downloadify(data, null, "FICHE CONSULTATION "+frm.doc.supplier_name);
		}
	
		
		
		
	},
	'importer_articles': function(frm){
	 var me = this;
		console.log("manufacturer : ",frm.doc.manufacturer)
					frappe.call({
					 method: 'erpnext.stock.doctype.material_request.material_request.get_supplier_quotation',
						args:{manufacturer: frm.doc.manufacturer},
					callback: function(r){
						//frappe.msgprint("Vous devez enregistrer pour filtrer les resultats");
						let res = [];
						r.message.map(w => {
							//console.log("api returning :",w)
							res.push(w.name);
						})
						//console.log("get supp",res);
						if(res){					
					erpnext.utils.map_current_doc({
						method: "erpnext.stock.doctype.material_request.material_request.make_supplier_quotation",
						source_doctype: "Material Request",
						predef: res,
						target: frm,
						setters: {
							company: frm.doc.company
						},
						get_query_filters: {
							material_request_type: "Purchase",
							docstatus: 1,
							status: ["!=", "Stopped"],
							per_ordered: ["<", 99.99]
						}
					});
						//frm.reload_doc();
							//frm.refresh();
							//frm.refresh_field("items");
							frappe.msgprint("Vous devez enregistrer pour filtrer les resultats  ")
						}}});	
	}, 
	validate: function(frm){
	
		if(frm.doc.manufacturer){ 
		var _items = [];	
		frm.doc.items.forEach(i => {
			console.log("validating ")
			
			if(i.fabricant == frm.doc.manufacturer){
				//	Object.keys(i);
				//.delete();
				 
				_items.push(i);
			
			}
		
		});
	
		frm.doc.items = _items;

		} 
	
	}

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
