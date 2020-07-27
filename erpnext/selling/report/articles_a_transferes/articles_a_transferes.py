# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):	
	columns, data = [], []
	if  not filters.warehouse:
		frappe.throw("Appliquer un entrepot cible ")
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
			"label": "Qts total a transferee",
			"width": 200
		})
	columns.append({
			"fieldname": "source",
			"label": "Stock Source Suggere",
			"width": 150
		})
	columns.append({
			"fieldname": "qty_source",
			"label": "Qts dans Stock Source",
			"width": 210
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
		if filters.warehouse  and item.warehouse and item.warehouse !=  filters.warehouse:
			continue
		if filters.grouped ==1:
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
		total_qty_cmd = sum(_item.qty for _item in items if (_item.qty and _item.item_code == item.item_code))
		qts_transfere = total_qty_cmd - qty
		if filters.grouped==1 and filters.warehouse:
			total_qty = total_qty_cmd
			parent =  ', '.join({_item.parent for _item in items if (_item.parent  and _item.item_code == item.item_code)})
			client =  ', '.join({_item.customer_name for _item in items if ("customer_name" in _item and _item.customer_name   and _item.item_code == item.item_code)})
			actual_qty  = '0'
			qts_transfere = total_qty - qty
			delivery_date = min(_item.schedule_date for _item in items if (_item.schedule_date  and _item.item_code == item.item_code)) if "consulted" in item else  min(_item.delivery_date for _item in items if _item.delivery_date  and _item.item_code == item.item_code)
		else:
			total_qty = item.qty
		added.append(item.item_code)
		qts_stock_source = 0
		suggere_qty = frappe.db.sql("""select warehouse,actual_qty from `tabBin` where item_code=%s and actual_qty>%s  and warehouse!=%s limit 1""",(item.item_code,qts_transfere,item.warehouse),as_dict=1)
		if not suggere_qty :
			suggere_qty = frappe.db.sql("""select warehouse,actual_qty from `tabBin` where item_code=%s and  actual_qty>0  and warehouse!=%s  order by actual_qty desc  limit 1""",(item.item_code, item.warehouse),as_dict=1)
			if suggere_qty and suggere_qty[0]:
				suggere_qty = suggere_qty[0]
				if filters.source_warehouse and filters.source_warehouse != suggere_qty.warehouse:
					continue
				
				suggere_qty = "Qts Insufisante | %s" % (suggere_qty.warehouse)
				qts_stock_source = suggere_qty.actual_qty
			else:
				suggere_qty = "Non disponible"
		else:
			suggere_qty = suggere_qty[0]
			if filters.source_warehouse and filters.source_warehouse != suggere_qty.warehouse:
					continue
			
			suggere_qty = "%s" % (suggere_qty.warehouse)
			qts_stock_source = suggere_qty.actual_qty
			
				
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
			suggere_qty,
			qts_stock_source,
			"",
			""
		]
	
		data.append(row)
	return columns, data
