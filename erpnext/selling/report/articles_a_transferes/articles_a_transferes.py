# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
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
			"fieldname": "qty_dispc",
			"label": "Qts disponible a la commande",
			"width": 220
		})
	columns.append({
			"fieldname": "qty_disp",
			"label": "Qts disponible maintenant",
			"width": 220
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
			"fieldname": "datet",
			"label": "Date de transfere",
			"width": 200
		})
	columns.append({
			"fieldname": "traite",
			"label": "Qts transferee",
			"width": 150
		})
	
	items = []
	orders_items = frappe.db.sql(""" select * from `tabSales Order Item` soi where soi.docstatus=1 and soi.delivered_qty=0 and soi.actual_qty < soi.qty 
	and soi.parent in (select so.name from `tabSales Order` so where so.docstatus = 1 and so.workflow_state='Reservation' and so.status not in ('Closed','Cancelled','Draft')) """,as_dict=1)
	
	
	items.extend(orders_items)
	dm_items = frappe.db.sql(""" select * from `tabMaterial Request Item` mri 
	left join (select mr.name,mr.material_request_type from `tabMaterial Request` mr where mr.docstatus = 1 and mr.material_request_type='Material Transfer') mrd
	on (mrd.name = mri.parent) where mri.docstatus=1 and mri.ordered_qty=0""",as_dict=1)
	
	items.extend(dm_items)
	
	for item in items:
		qty = frappe.db.sql("""select sum(actual_qty) from `tabBin` where item_code=%s and warehouse=%s""",(item.item_code,item.warehouse))[0]
		if qty and qty[0]:
			qty = qty[0]
		else:
			qty = 0
		if item.qty <= qty:
			continue
		#qts a transfere
		qts_transfere = item.qty - qty
		delivery_date = ''
		#material request
		if hasattr(item, 'schedule_date'):
			delivery_date = item.schedule_date
			
		else:
			delivery_date = item.delivery_date
		
		row = [
			delivery_date,
			item.item_code,
			item.item_name,
			item.ref_fabricant,
			item.fabricant,
			item.parent,
			item.warehouse,
			item.qty,
			item.actual_qty,
			qty or 'NA',
			qts_transfere,
			"",
			"",
			"",
			""
		]
	
	data.append(row)
	return columns, data