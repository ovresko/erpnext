// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Rapport Analyse Consultation"] = {
	"filters": [
	{
		"fieldname": "article_consulted",
		"label": __("Articles Consultés Seulement"),
		"fieldtype": "Check",
		"default": 1
	}
	]
}
