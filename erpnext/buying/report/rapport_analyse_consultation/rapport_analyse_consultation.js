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
		"fieldname": "consultation_interne",
		"label": __("Consultation interne"),
		fieldtype: "Link",
		options: "Supplier Quotation", 
		"get_query": function() {
			return {
				"doctype": "Supplier Quotation",
				"filters": {
					"etat_consultation_deux": "Consultation Interne",
				}
			}
		}
	},
	{
		"fieldname": "consultation_externe",
		"label": __("Consultation externe"),
		fieldtype: "Link",
		options: "Supplier Quotation", 
		"get_query": function() {
			return {
				"doctype": "Supplier Quotation",
				"filters": {
					"etat_consultation_deux": "Consultation Externe",
				}
			}
		}
	}
		
	]
}
