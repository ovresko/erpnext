
function delete_item(data) {
	console.log(data);
	var confirme = confirm("Confirmer l'operation ?");
	if(!confirme){
		return;
	}
	frappe.call({
			method: "erpnext.stock.doctype.item.item.delete_order_item",
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

frappe.query_reports["Etat Reliquats Clients"] = {
"filters" : [
{"fieldname": "customer",
"label": "Client",
"fieldtype":"Link",
"options":"Customer",
"default":"NA"
}
]

}
