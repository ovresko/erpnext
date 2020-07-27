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
		}
		,{
			"fieldname": "grouped",
			"label": "Grouper les qts",
			"fieldtype": "Check",
			"default": 1
		}
	]
}
