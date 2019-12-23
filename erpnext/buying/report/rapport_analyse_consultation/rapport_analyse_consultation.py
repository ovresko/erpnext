# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.stock.get_item_details import get_item_details


def execute(filters=None):
	columns, data = [], []
	columns.append({
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		})
	

	columns.append({
			"fieldname": "item_name",
			"label": _("Item Name"),
			"width": 150
		})
	columns.append({
			"fieldname": "material_request",
			"label": _("Material Request"),
			"fieldtype": "Link",
			"options": "Material Request",
			"width": 80
		})
	columns.append({
			"fieldname": "supplier_quotation",
			"label": _("Consultation"),
			"fieldtype": "Link",
			"options": "Supplier Quotation",
			"width": 80
		})
	columns.append({
			"fieldname": "fabricant",
			"label": _("Fabricant"),
			"width": 80
		})
	columns.append({
			"fieldname": "ref_fabricant",
			"label": _("Ref Fabricant"),
			"width": 80
		})
	columns.append({
			"fieldname": "qts_demande",
			"label": _("Qte Demandee"),
			"width": 100
		})
	columns.append({
			"fieldname": "qts_demande_modele",
			"label": _("Qte Demandee Modele"),
			"width": 180
		})
	columns.append({
			"fieldname": "qts_reliquat",
			"label": _("Qte reliquats"),
			"width": 80
		})
	columns.append({
			"fieldname": "qts_reliquat_modele",
			"label": _("Qte reliquats Modele"),
			"width": 80
		})
	columns.append({
			"fieldname": "qts_variante_stock",
			"label": _("Qte Variante En Stock"),
			"width": 80
		})
	columns.append({
			"fieldname": "qts_projete",
			"label": _("Qte Projete"),
			"width": 80
		})
	columns.append({
			"fieldname": "qts_max_achat",
			"label": _("Qte Max d'achat"),
			"width": 80
		})
	columns.append({
			"fieldname": "qts_a_commande",
			"label": "Qte a commandee (demandees - projte)",
			"width": 80
		})
	columns.append({
			"fieldname": "qts_a_commande_modele",
			"label": "Qte a commandee par modele (demandees - projte)",
			"width": 80
		})
	columns.append({
			"fieldname": "last_purchase_rate",
			"label": "Dernier Prix d'achat",
			"width": 80
		})
	columns.append({
			"fieldname": "last_purchase_rate",
			"label": "Dernier Prix d'achat (Devise)",
			"width": 80
		})
	columns.append({
			"fieldname": "last_purchase_rate",
			"label": "Dernier Prix d'achat (Devise)",
			"width": 80
		})
	
	price_lists= frappe.get_all("Price List",filters={"buying":1},fields=["name","currency"])
	if price_lists:
		for pl in price_lists:
			columns.append({
				"fieldname": pl.name,
				"label": pl.name,
				"width": 80
			})
			
	mris = frappe.get_all("Material Request Item",filters={"docstatus":1,"consulted" : filters.article_consulted}, fields=["last_purchase_rate","max_order_qty","projected_qty","actual_qty","stock_qty","ordered_qty","name","item_code","item_name","parent","consultation","fabricant","ref_fabricant"])
	for mri in mris:
		last_purchase_devise = frappe.get_value('Item', mri.item_code, 'last_purchase_devise')
		modele_stock_qty = sum([a.stock_qty for a in mris if a.model == mri.model])
		modele_ordered_qty = sum([a.ordered_qty for a in mris if a.model == mri.model])
		qts_a_commande = mri.stock_qty - mri.projected_qty
		modele_qts_a_commande =  mri.stock_qty - modele_ordered_qty
		row = [mri.item_code,
		       mri.item_name,
		       mri.parent,
		       mri.consultation,
		       mri.fabricant,
		       mri.ref_fabricant,
		       mri.stock_qty,
		       modele_stock_qty,
		       mri.ordered_qty,
		       modele_ordered_qty,
		       mri.actual_qty,
		       mri.projected_qty,
		       mri.max_order_qty,
		       qts_a_commande,
		       modele_qts_a_commande,
		       mri.last_purchase_rate,
		       last_purchase_devise]
		
		# get prices in each price list
		if price_lists:
			for pl in price_lists:
				if pl.name:
					price = frappe.db.sql("""select price_list_rate from `tabItem Price` where price_list=%s and item_code=%s""",(pl.name,mri.item_code))
					if price:
						row.append(price)
					else:
						row.append(0)
				else:
					row.append(0)
		
		data.append(row)
		
	return columns, data
