# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe import _, _dict
from erpnext.stock.get_item_details import get_item_details

def execute(filters=None):
	columns, data = [], []
	if not filters.group and not filters.variant_of and not filters.modele_vehicule and not filters.version and not filters.manufacturer:
		frappe.msgprint("Appliquer un filtre")
		return columns, data
	columns.append({
			"fieldname": "item_code",
			"label": _("Item Code"),
			"width": 150
		})
	columns.append({
			"fieldname": "item_name",
			"label": _("Item Name"),
			"width": 150
		})
	columns.append({
			"fieldname": "fabricant",
			"label": _("Fabricant"),
			"width": 150
		})
	columns.append({
			"fieldname": "ref_fabricant",
			"label": _("Ref Fabricant"),
			"width": 150
		})
	columns.append({
			"fieldname": "qts_reliquat",
			"label": _("Qte reliquats"),
			"width": 160
		})
	columns.append({
			"fieldname": "qts",
			"label": _("Qte"),
			"width": 150
		})
	columns.append({
			"fieldname": "qts_projete",
			"label": _("Qte Projete"),
			"width": 150
		})
	columns.append({
			"fieldname": "qts_max_achat",
			"label": _("Qte Max d'achat"),
			"width": 150
		})
	columns.append({
			"fieldname": "last_purchase_rate",
			"label": "Dernier Prix d'achat (DZD)",
			"width": 150
		})
	columns.append({
			"fieldname": "last_purchase_devise",
			"label": "Dernier Prix d'achat (Devise)",
			"width": 150
		})

	price_lists= frappe.get_all("Price List",filters={"buying":1},fields=["name","currency"])
	if price_lists:
		for pl in price_lists:
			columns.append({
				"fieldname": pl.name,
				"label": "%s (%s)" % (pl.name,pl.currency),
				"width": 150
			})
	mris = []

	order_by_statement = "order by item_code"
	items = frappe.db.sql(
		"""
		select
			variant_of,has_variants,item_name, item_code, manufacturer,last_purchase_rate , manufacturer_part_no, item_group,last_purchase_devise,max_order_qty,max_ordered_variante
		from `tabItem`
		where disabled=0 {conditions}
		{order_by_statement}
		""".format(
			conditions=get_conditions(filters),
			order_by_statement=order_by_statement
		),
		filters, as_dict=1)
	for mri in items:
		global info
		qts_max_achat = 0
		if mri.variant_of:
			#variante
			info = info_variante(mri.item_code)
			qts_max_achat = mri.max_ordered_variante
		elif mri.has_variants:
			info = info_modele(mri.item_code)
			qts_max_achat = mri.max_order_qty
		
		row = [mri.item_code,
		       mri.item_name,
		       mri.manufacturer,
		       mri.manufacturer_part_no,
		       #qts_reliquat
		       info[3],
		       #qts
		       info[0],
		       #qts_projete
		       info[2],
		       #qts_max_achat
		       qts_max_achat,
		       #last_purchase_rate
		       mri.last_purchase_rate,
		       #last_purchase_devise
		       mri.last_purchase_devise
		      ]
		
		# get prices in each price list
		if price_lists and not mri.has_variants:
			for pl in price_lists:
				if pl.name:
					price = frappe.db.sql("""select price_list_rate from `tabItem Price` where buying=1 and price_list=%s and (  item_code=%s) ORDER BY creation DESC LIMIT 1;""",(pl.name,mri.item_code))
					if price:
						row.append(price[0][0])
					else:
						row.append("_")
				else:
					row.append("_")
		
		data.append(row)
		
	return columns, data
					       
def get_conditions(filters):
	conditions = []
	# group, modele, manufacturer, age_plus, age_minus
	if filters.get('group'):
		conditions.append("item_group=%(group)s")
	if filters.get('variant_of'):
		conditions.append("(item_code=%(variant_of)s or variant_of=%(variant_of)s)")
	if filters.get('is_purchase'):	
		conditions.append("is_purchase_item=1")
	if filters.get('version'):
		conditions.append("""item_code in (select parent from `tabVersion vehicule item`
		where version_vehicule=%s)""" % (filters.version))
	if filters.get('modele_vehicule'):
		modele_vehicule = frappe.get_doc('Modele de vehicule',filters.modele_vehicule)
		if modele_vehicule:
			conditions.append("""item_code in (select parent from `tabVersion vehicule item`
		where modele_vehicule=%s)""" % (modele_vehicule.modele))
	#if filters.get('modele'):
	#	conditions.append("(variant_of=%(modele)s or item_code=%(modele)s)")
	
	if filters.get('manufacturer'):
		conditions.append("manufacturer=%(manufacturer)s")

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def info_modele(model, warehouse=None):
	values, condition = [model], ""
	if warehouse:
		values.append(warehouse)
		condition += " AND warehouse = %s"

	actual_qty = frappe.db.sql("""select sum(actual_qty), sum(indented_qty), sum(projected_qty), sum(ordered_qty) from tabBin
		where model=%s {0}""".format(condition), values)[0]

	return actual_qty

def info_variante(model, warehouse=None):
	values, condition = [model], ""
	if warehouse:
		values.append(warehouse)
		condition += " AND warehouse = %s"

	actual_qty = frappe.db.sql("""select sum(actual_qty), sum(indented_qty), sum(projected_qty), sum(ordered_qty) from tabBin
		where item_code=%s {0}""".format(condition), values)[0]

	return actual_qty
