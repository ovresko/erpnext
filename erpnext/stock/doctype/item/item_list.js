frappe.listview_settings['Item'] = {
	add_fields: ["item_name", "stock_uom", "item_group", "image", "variant_of",
		"has_variants", "end_of_life", "disabled"],
	filters: [["disabled", "=", "0"]],
	onload: function(listview) {
		listview.page.add_menu_item("Creer Catalogue", function() {
			var names=[];
			const selected_docs = listview.get_checked_items(true);
			for (let doc of selected_docs) {
				names.push(doc);
			}
			//$.each(listview.get_checked_items(), function(key, value){
			//	names.push(value._name);
			//});
			var w = window.open("/api/method/erpnext.stock.doctype.item.item.bulk_print_list?"
							+"names="+encodeURIComponent(names));
	
			if(!w) {
				frappe.msgprint(__("Please enable pop-ups")); return;
			}
		});
	},
	get_indicator: function(doc) {
		if (doc.disabled) {
			return [__("Disabled"), "grey", "disabled,=,Yes"];
		} else if (doc.end_of_life && doc.end_of_life < frappe.datetime.get_today()) {
			return [__("Expired"), "grey", "end_of_life,<,Today"];
		} else if (doc.has_variants) {
			return [__("Template"), "orange", "has_variants,=,Yes"];
		} else if (doc.variant_of) {
			return [__("Variant"), "green", "variant_of,=," + doc.variant_of];
		}
	},

	reports: [
		{
			name: 'Stock Summary',
			report_type: 'Page',
			route: 'stock-balance'
		},
		{
			name: 'Stock Ledger',
			report_type: 'Script Report'
		},
		{
			name: 'Stock Balance',
			report_type: 'Script Report'
		},
		{
			name: 'Stock Projected Qty',
			report_type: 'Script Report'
		}

	]
};

frappe.help.youtube_id["Item"] = "qXaEwld4_Ps";
