// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Rapport Analyse Consultation"] = {
	"filters": [
	{
		"fieldname": "article_consulted",
		"label": __("Avec Devis / Sans Devis"),
		"fieldtype": "Check",
		"default": 1
},
	{
		"fieldname":"from_date",
		"label": __("From Date"),
		"fieldtype": "Date",
		"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		"width": "80"
	},
	{
		"fieldname": "fabricant",
		"label": __("Fabricant"),
		fieldtype: "Link",
		options: "Manufacturer",
	},
	{
		"fieldname": "consultation",
		"label": __("Consultation"),
		fieldtype: "Link",
		options: "Supplier Quotation",
	}
		
	]
}
