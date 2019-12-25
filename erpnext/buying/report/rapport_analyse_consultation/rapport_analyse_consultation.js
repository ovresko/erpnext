// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Rapport Analyse Consultation"] = {
	"filters": [
	{
		"fieldname": "article_consulted",
		"label": __("Avec Devis / Sans Devis"),
		"fieldtype": "Check",
		"default": 0
	},
	{
		"fieldname":"from_date",
		"label": __("From Date"),
		"fieldtype": "Date",
		"default": frappe.datetime.add_days(frappe.datetime.get_today(), -10),
		"width": "80"
	},
	{
		"fieldname": "demande",
		"label": __("Demande de materiel"),
		fieldtype: "Link",
		options: "Material Request", 
	},
	{
		"fieldname": "consultation",
		"label": __("Consultation"),
		fieldtype: "Link",
		options: "Supplier Quotation", 
	}
		
	]
}
