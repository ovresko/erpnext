// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Articles a transferes"] = {
	"filters": [
		{
			"fieldname": "warehouse",
			"label": "Stock Cible",
			fieldtype: "Link",
			options: "Warehouse"
		},
		{
			"fieldname": "source_warehouse",
			"label": "Stock Source",
			fieldtype: "Link",
			options: "Warehouse"
		}
		,{
			"fieldname": "grouped",
			"label": "Grouper les qts",
			"fieldtype": "Check",
			"default": 0
		},{
			"fieldname": "disp",
			"label": "Disponible seulement",
			"fieldtype": "Check",
			"default": 1
		}
	]
}
