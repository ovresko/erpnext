# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	
	columns.append({
			"fieldname": "name",
			"label": "Commande",
			"width": 200
		})
	columns.append({
			"fieldname": "delivery_date",
			"label": "Date Livraison",
			"width": 200
		})
	columns.append({
			"fieldname": "customer_name",
			"label": "Client",
			"width": 200
		})
	columns.append({
			"fieldname": "customer",
			"label": "Client",
			"width": 200
		})
	columns.append({
			"fieldname": "item_code",
			"label": "Article",
			"width": 200
		})
	columns.append({
			"fieldname": "ref_fabricant",
			"label": "Ref Fabricant",
			"width": 200
		})
	columns.append({
			"fieldname": "fabricant",
			"label": "Fabricant",
			"width": 200
		})
	columns.append({
			"fieldname": "qty",
			"label": "Qts commandee",
			"width": 200
		})
	columns.append({
			"fieldname": "delivered_qty",
			"label": "Qts livree",
			"width": 200
		})
	columns.append({
			"fieldname": "reste",
			"label": "Reliquat",
			"width": 200
		})
	columns.append({
			"fieldname": "status",
			"label": "Status",
			"width": 200
		})
	columns.append({
			"fieldname": "delete",
			"label": "Opt",
			"width": 120
		})
	
	orders_items = frappe.db.sql("""select 
					mr.name,
					mr.delivery_date ,
					mr.customer_name ,
					mr.customer ,
					mri.item_code ,
					mri.ref_fabricant ,
					mri.fabricant ,
					mri.qty ,
					mri.delivered_qty ,
					@reste :=(mri.qty - mri.delivered_qty) ,
					mr.status
					from `tabSales Order` mr 
					left join `tabSales Order Item` mri 
					on mr.name = mri.parent
					where mr.docstatus = 1 and mr.status != 'Closed' 
					and mr.status != 'Completed' 
					and mri.delivered_qty < mri.qty 
					and (mr.customer=%(customer)s OR %(customer)s IS NULL OR %(customer)s ='NA') """,filters,as_dict=1)
	
	for item in orders_items:
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
			"""<button onClick="delete_item('%s')" type='button'>Supprimer</button>""" % (item.name)
		]
	
		data.append(row)
	
	return columns, data
