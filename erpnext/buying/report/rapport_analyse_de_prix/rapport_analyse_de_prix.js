// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Rapport Analyse de prix"] = {
	"filters": [
		{
			"fieldname":"group",
			"label": __("Groupe Article"),
			"fieldtype": "Link",
			"options": "Item Group"
		},
	]
}
