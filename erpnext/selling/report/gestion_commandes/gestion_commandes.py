# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	if  not filters.customer:
		frappe.throw("Selectionner un client")
		return columns, data
	
	columns.append({
			"fieldname": "date",
			"label": "Date",
			"width": 200
		})
	columns.append({
			"fieldname": "item",
			"label": "Article",
			"width": 200
		})
	columns.append({
			"fieldname": "item_name",
			"label": "Designation",
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
			"fieldname": "client",
			"label": "Client",
			"width": 150
		})
	columns.append({
			"fieldname": "commande",
			"label": "Commande",
			"width": 150
		})
	columns.append({
			"fieldname": "warehouse",
			"label": "Stock",
			"width": 150
		})
	columns.append({
			"fieldname": "qty_disp",
			"label": "Qts disponible maintenant",
			"width": 220
		})
	columns.append({
			"fieldname": "qty_total",
			"label": "Qts Commande",
			"width": 150
		})
	columns.append({
			"fieldname": "qty_prep",
			"label": "Qts a preparee",
			"width": 150
		})
	
	items = []
	orders_items = frappe.db.sql(""" select * from `tabSales Order Item` soi   
	left join (select customer_name as customer_name,customer, name,status,docstatus,workflow_state,delivery_date as delivery_date from `tabSales Order` ) so  
	on (soi.parent = so.name)
	where so.status not in ('Closed','Cancelled','Draft') and so.customer=%s and so.docstatus = 1 and so.workflow_state='Reservation' and soi.docstatus=1  and soi.parent is not null""",(filters.customer),as_dict=1)
	
	
	items.extend(orders_items)
	for item in items:
		qty = frappe.db.sql("""select sum(actual_qty) from `tabBin` where item_code=%s and warehouse=%s""",(item.item_code,item.warehouse))[0]
		if qty and qty[0]:
			qty = qty[0]
		else:
			qty = 0
		if qty < 0:
			qty = 0
		row = [
			item.delivery_date,
			item.item_code,
			item.item_name,
			item.ref_fabricant,
			item.fabricant,
			item.customer_name,
			item.parent,
			item.warehouse,
			qty,
			item.qty,
			item.qty - item.delivered_qty
		]
	
		data.append(row)
	return columns, data
