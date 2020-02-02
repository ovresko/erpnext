// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Rapport analyse de besoin"] = {
	"filters": [
		{
		"fieldname": "group",
		"label": __("Item Group"),
		fieldtype: "Link",
		options: "Item Group"
	}
	]
}
