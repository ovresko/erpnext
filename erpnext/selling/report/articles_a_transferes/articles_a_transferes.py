# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns.append({
			"fieldname": "item",
			"label": "Article",
			"width": 200
		})
	columns.append({
			"fieldname": "item_ref",
			"label": "Reference",
			"width": 150
		})
	columns.append({
			"fieldname": "fabricant",
			"label": "Fabricant",
			"width": 150
		})
	columns.append({
			"fieldname": "document",
			"label": "Transfere pour",
			"width": 150
		})
	columns.append({
			"fieldname": "warehouse",
			"label": "Stock",
			"width": 150
		})
	columns.append({
			"fieldname": "qty_total",
			"label": "Qts besoin total",
			"width": 150
		})
	columns.append({
			"fieldname": "qty_disp",
			"label": "Qts disponible",
			"width": 150
		})
	columns.append({
			"fieldname": "qty",
			"label": "Qts a transferee",
			"width": 150
		})
	columns.append({
			"fieldname": "source",
			"label": "Stock Source Suggere",
			"width": 150
		})
	columns.append({
			"fieldname": "qty_source",
			"label": "Qts dans Stock Source",
			"width": 150
		})
	columns.append({
			"fieldname": "date",
			"label": "Date de transfere",
			"width": 200
		})
	columns.append({
			"fieldname": "traite",
			"label": "Qts transferee",
			"width": 150
		})
	
	orders_items = frappe.db.sql(""" select * from `tabSales Order Item` soi where soi.docstatus=1 and soi.delivered_qty=0 and soi.actual_qty < soi.qty 
	and soi.parent not in (select so.name from `tabSales Order` so where so.docstatus = 1 and so.status in ('Closed','Cancelled','Draft')) """,as_dict=1)
	for item in orders_items:
		row = [
			item.item_code,
			item.ref_fabricant,
			item.fabricant,
			item.parent,
			item.warehouse,
			item.qty,
			item.actual_qty,
			(item.qty - item.actual_qty),
			"",
			"",
			"",
			""
		]
	
	data.append(row)
	return columns, data
