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
	'importer_articles': function(frm){
	 load_fab();	
	},
	validate: function(frm){
	
		if(frm.doc.manufacturer){
		
		
		
		var _items = [];	
		frm.doc.items.forEach(i => {
			
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

function load_fab(){
	
var me= this;
					frappe.call({
					 method: 'erpnext.stock.doctype.material_request.material_request.get_supplier_quotation',
					callback: function(r){
						let res = [];
						r.message.map(w => {
							res.push(w.name);
						})
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
					load_fab();
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
