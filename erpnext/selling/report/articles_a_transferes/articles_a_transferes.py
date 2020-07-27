# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):	
	columns, data = [], []
	if filters.get("grouped") and not filters.get("warehouse"):
		frappe.msgprint("Appliquer un entrepot cible pour regrouper")
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
			"fieldname": "document",
			"label": "Transfere pour",
			"width": 150
		})
	columns.append({
			"fieldname": "client",
			"label": "Client",
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
	orders_items = frappe.db.sql(""" select * from `tabSales Order Item` soi   
	left join (select customer_name as customer_name, name,status,docstatus,workflow_state,delivery_date as delivery_date from `tabSales Order` ) so  
	on (soi.parent = so.name)
	where so.status not in ('Closed','Cancelled','Draft') and so.docstatus = 1 and so.workflow_state='Reservation' and soi.docstatus=1 and soi.delivered_qty=0 and soi.actual_qty < soi.qty and soi.parent is not null	
	""",as_dict=1)
	
	
	items.extend(orders_items)
	dm_items = frappe.db.sql(""" select * from `tabMaterial Request Item` mri 
	left join (select docstatus,name,material_request_type,status from `tabMaterial Request`) mrd
	on (mrd.name = mri.parent) 
	where  mrd.docstatus = 1 and mrd.material_request_type='Material Transfer' and mrd.status in ('Submitted','Pending') and mri.parent is not null and mri.docstatus=1 and mri.ordered_qty=0""",as_dict=1)
	
	items.extend(dm_items)
	added = []
	for item in items:
		if filters.get("warehouse") and item.warehouse and item.warehouse !=  filters.get("warehouse"):
			continue
		if filters.get("grouped") and filters.get("warehouse"):
			if item.item_code in added:
				continue
		qty = frappe.db.sql("""select sum(actual_qty) from `tabBin` where item_code=%s and warehouse=%s""",(item.item_code,item.warehouse))[0]
		if qty and qty[0]:
			qty = qty[0]
		else:
			qty = 0
		
		#if item.qty <= qty:
		#	continue
		#qts a transfere
		qts_transfere = item.qty - qty
		delivery_date = ''
		parent = ''
		client = ''
		actual_qty = item.actual_qty
		#material request
		if "consulted" in item:
			delivery_date = item.schedule_date or 'NA'
			parent = item.parent			
		else:
			delivery_date = item.delivery_date or 'NC'
			client = item.customer_name
			parent = item.parent
			
		total_qty = 0
		if filters.get("grouped") and filters.get("warehouse"):
			total_qty = sum(item.qty for item in items if item.qty)
			parent =  ', '.join({item.parent for item in items if item.parent})
			client =  ', '.join({item.customer_name for item in items if ("customer_name" in item and item.customer_name)})
			actual_qty  = sum(item.actual_qty for item in items if item.actual_qty)
			qts_transfere = total_qty - qty
			delivery_date = min(item.schedule_date for item in items if item.schedule_date) if "consulted" in item else  min(item.delivery_date for item in items if item.delivery_date)
		else:
			total_qty = item.qty
		added.append(item.item_code)
		row = [
			delivery_date,
			item.item_code,
			item.item_name,
			item.ref_fabricant,
			item.fabricant,
			parent,
			client,
			item.warehouse,
			total_qty,
			actual_qty,
			qty,
			qts_transfere,
			"",
			"",
			"",
			""
		]
	
		data.append(row)
	return columns, data
