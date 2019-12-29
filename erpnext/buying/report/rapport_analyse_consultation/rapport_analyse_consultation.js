// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Rapport Analyse Consultation"] = {
	"filters": [ 
	{
		"fieldname":"from_date",
		"label": __("From Date"),
		"fieldtype": "Date",
		"default": frappe.datetime.add_days(frappe.datetime.get_today(), -60),
		"width": "80"
	},
	 
	{
		"fieldname": "demande",
		"label": __("Demande de materiel"),
		fieldtype: "Link",
		options: "Material Request", 
		"get_query": function() {
			return {
				"doctype": "Material Request",
				"filters": {
					"status": "Pending",
				}
			}
		}
		
		
	},
	{
		"fieldname": "consultation",
		"label": __("Consultation"),
		fieldtype: "Link",
		options: "Supplier Quotation", 
		"get_query": function() {
			return {
				"doctype": "Supplier Quotation",
				"filters": {
					"docstatus": 0,
				}
			}
		}
	}
		
	]
}
