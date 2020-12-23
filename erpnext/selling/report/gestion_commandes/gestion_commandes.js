// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Gestion Commandes"] = {
	"filters": [
		{
			"fieldname": "customer",
			"label": "Client",
			fieldtype: "Link",
			options: "Customer"
		}
	]
}
