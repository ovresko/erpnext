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
		},
		{
			"fieldname": "modele",
			"label": __("Modele de vehicule"),
			fieldtype: "Link",
			options: "Modele de vehicule"
		},
		{
			"fieldname": "manufacturer",
			"label": __("Manufacturer"),
			fieldtype: "Link",
			options: "Manufacturer",
			"get_query": function() {
			return {
				"doctype": "Manufacturer",
				"filters": {
					"actif": 1,
					   }
				}
			}
		},
		{
			"fieldname":"age_plus",
			"label": __("Age plus que"),
			"fieldtype": "Select",
			"options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"],
			"default": ""
		},
		{
			"fieldname":"age_minus",
			"label": __("Age moin que"),
			"fieldtype": "Select",
			"options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"],
			"default": ""
		}
	]
}