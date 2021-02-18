# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	
	if not filters.customer:
		filters.customer = "NA"
	
	columns.append({
			"fieldname": "name",
			"label": "Commande",
			"width": 100
		})
	columns.append({
			"fieldname": "delivery_date",
			"label": "Date Livraison",
			"width": 100
		})
	columns.append({
			"fieldname": "customer_name",
			"label": "Client",
			"width": 150
		})
	columns.append({
			"fieldname": "customer",
			"label": "Client",
			"width": 110
		})
	columns.append({
			"fieldname": "item_code",
			"label": "Article",
			"width": 110
		})
	columns.append({
			"fieldname": "ref_fabricant",
			"label": "Ref Fabricant",
			"width": 140
		})
	columns.append({
			"fieldname": "fabricant",
			"label": "Fabricant",
			"width": 100
		})
	columns.append({
			"fieldname": "qty",
			"label": "Qts commandee",
			"width": 90
		})
	columns.append({
			"fieldname": "delivered_qty",
			"label": "Qts livree",
			"width": 100
		})
	columns.append({
			"fieldname": "reste",
			"label": "Reliquat",
			"width": 100
		})
	columns.append({
			"fieldname": "status",
			"label": "Status",
			"width": 70
		})
	columns.append({
			"fieldname": "info",
			"label": "Opt",
			"width": 110
		})
	columns.append({
			"fieldname": "delete",
			"label": "Opt",
			"width": 110
		})
	
	orders_items = frappe.db.sql("""select 
					mr.name,
					mri.name as mriname,
					mr.delivery_date ,
					mr.customer_name ,
					mr.customer ,
					mri.item_code ,
					mri.ref_fabricant ,
					mri.fabricant ,
					mri.qty ,
					mri.delivered_qty ,
					@reste := (mri.qty - mri.delivered_qty) as reste,
					mr.status
					from `tabSales Order` mr 
					left join `tabSales Order Item` mri 
					on mr.name = mri.parent
					where mr.docstatus = 1 and mr.status != 'Closed' 
					and mr.status != 'Completed' 
					and mri.delivered_qty < mri.qty 
					and (mr.customer=%(customer)s OR %(customer)s IS NULL OR %(customer)s ='NA') """,filters,as_dict=1)
	
	for item in orders_items:
		has_bl = frappe.db.sql("""select sum(dni.qty) as qty, dn.name as name, dni.name as dniname,dni.item_code,dni.parent,dn.customer from 'tabDelivery Note Item' dni
		left join 'tab Delivery Note' dn
		on dn.name == dni.parent
		where dn.docstatus = 0 and dn.customer='%s' and dni.item_code='%s'  """ % (filters.customer, item.item_code),as_dict=1)
		delete = ""
		if has_bl and has_bl[0] and has_bl[0].qty:
			delete = "En preparation %s" % has_bl[0].name
		else:
			delete = """<button onClick="delete_item('%s')" type='button'>Supprimer</button>""" % (item.mriname)
		row = [
			item.name,
			item.delivery_date,
			item.customer_name,
			item.customer,
			item.item_code,
			item.ref_fabricant,
			item.fabricant,
			item.qty,
			item.delivered_qty,
			item.reste,
			item.status,
			"""<input type='button' onclick="erpnext.utils.open_item_info('%s', this)" value='info'>  </input>""" % (item.item_code),
			delete
		]
	
		data.append(row)
	
	return columns, data
