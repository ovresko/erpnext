# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import timedelta
from frappe.utils import get_datetime
from frappe.utils import get_fullname,today,cstr, flt, getdate, comma_and, cint, nowdate, add_days


def execute(filters=None):
	columns, data = [], []
	if  not filters.from_date:
		frappe.throw("Selectionner date")
		return columns, data
	
	columns.append({
			"fieldname": "date",
			"label": "Date",
			"width": 200
		})
	columns.append({
			"fieldname": "date_fin",
			"label": "Date Fin",
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
			"fieldname": "clientc",
			"label": "Client",
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
			"fieldname": "item_commande",
			"label": "Art. Commande",
			"width": 150
		})
	columns.append({
			"fieldname": "commercial",
			"label": "Commercial",
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
	
	if not filters.from_date or not filters.to_date:
		frappe.throw("Date invalide")
		
	filters.from_date = getdate(filters.from_date)
	filters.to_date = getdate(filters.to_date)

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be greater than To Date"))
		
	items = []
	today = getdate(add_days(nowdate(), -15))

	orders_items = frappe.db.sql(""" select * from `tabSales Order Item` soi   
	left join (select customer_name as customer_name,customer, name as so_name,shipping_rule,owner,status,docstatus,workflow_state,delivery_date as delivery_date from `tabSales Order` ) so  
	on (soi.parent = so.so_name)
	where so.status not in ('Closed','Cancelled','Draft') {conditions} and soi.delivered_qty < soi.qty and so.docstatus = 1 and so.workflow_state='Reservation' and soi.docstatus=1  and soi.parent is not null """.format(
			conditions=get_conditions(filters)
		),filters,as_dict=1)


	commandes = set()
	items.extend(orders_items)
	for item in items:
		qty = frappe.db.sql("""select sum(actual_qty) from `tabBin` where item_code=%s and warehouse=%s""",(item.item_code,item.warehouse))[0]
		if qty and qty[0]:
			qty = qty[0]
		else:
			qty = 0
		if qty < 0:
			qty = 0
			
		if filters.get("disp") and qty <= 0:
			continue
			
		delivery = frappe.db.sql(""" select item_code from `tabDelivery Note Item` soi   
 		where soi.docstatus = 0 and soi.from_report =1 and soi.so_detail = %s""",(item.name),as_dict=1)

		if delivery and len(delivery):
			continue
		
		commandes.add(item.parent)
		datef = get_datetime(item.delivery_date) + timedelta(days=15)
		commerical = get_fullname(item.owner) or ''
		row = [
			item.delivery_date,
			datef,
			item.item_code,
			item.item_name,
			item.ref_fabricant,
			item.fabricant,
			item.customer,
			item.customer_name,
			item.parent,
			item.name,
			commerical,
			item.warehouse,
			qty,
			item.qty,
			item.qty - item.delivered_qty
		]
	
		data.append(row)
	commandes = " - ".join(commandes)
	data.append(["Liste des commandes",commandes,"_","_","_","_","_","_","_","_","_"])
	
	return columns, data

def get_conditions(filters):
	conditions = []

	#perfection
	if filters.get('customer'):
		conditions.append("so.customer=%(customer)s")
	
	#perfection
	if filters.get('user'):
		conditions.append("so.owner=%(user)s")
	if filters.get('regle'):
		conditions.append("so.shipping_rule=%(regle)s")	
		
	if filters.get('cmd'):
		conditions.append("so.so_name=%(cmd)s")
	if filters.get('from_date'):
		conditions.append("soi.delivery_date >= %(from_date)s")
	if filters.get('to_date'):
		conditions.append("soi.delivery_date <= %(to_date)s")
		
	return "and {}".format(" and ".join(conditions)) if conditions else ""





