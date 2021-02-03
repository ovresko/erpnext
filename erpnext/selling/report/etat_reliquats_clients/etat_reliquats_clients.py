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
	
	orders_items = frappe.db.sql(""" select 
					mr.name as "Commande:Link/Sales Order:Data:50",
					mr.delivery_date as "Date de livraison:Data:100",
					mr.customer_name as "Client:Data:160",
					mr.customer as "ID Client:Link/Customer:100",
					mri.item_code as "Article:Data:140",
					mri.ref_fabricant as "Ref Fabricant:Data:100",
					mri.fabricant as "Fabricant:Data:100",
					mri.qty as "Qts commandee:Data:100",
					mri.delivered_qty as "Qts livree:Data:100",
					@reste :=(mri.qty - mri.delivered_qty) as "Reliquat:Data:100",
					mr.status as "Status:Data:50"
				from `tabSales Order` mr 
				left join `tabSales Order Item` mri 
				on mr.name = mri.parent
				where mr.docstatus = 1 and mr.status != 'Closed' 
				and mr.status != 'Completed' 
				and mri.delivered_qty < mri.qty 
				and (mr.customer=%(customer)s OR %(customer)s IS NULL OR %(customer)s ='NA') """),filters,as_dict=1)
	
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
