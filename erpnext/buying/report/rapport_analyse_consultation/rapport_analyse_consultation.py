# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns.append({
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options": "Item"
		})
	
	mris = frappe.get_all("Material Request Item",filters={"docstatus":1,"material_request_type": "Purchase","consulted" : 0,"status": ("!=", "Stopped")}, fields=["name","item_code","item_name"])
	for mri in mris:
		data.append([mri.item_code])
		
	return columns, data
