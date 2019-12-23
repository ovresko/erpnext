# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns.append({
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		})
	#	mr_item.item_name as "Item Name::250",
	#	mr_item.item_code as "Code Article:Link/Item:120",
#	mr_item.item_name as "Item Name::250",
#	mr.name as "DM:Link/Material Request:80",
##	mr_item.consultation as "Consultation::100",
#	mr_item.fabricant as "Fabricant::70",
#	mr_item.ref_fabricant as "Ref Fabricant::100",
#
##	sum(ifnull(mr_item.stock_qty, 0)) as "Qté demandé:Float:100", 
#	sum(ifnull(mr_item.ordered_qty, 0)) as "Qté reliquats:Float:120", 
#	sum(ifnull(mr_item.actual_qty, 0)) as "Qté Variante En Stock:Float:100", 
#	sum(ifnull(mr_item.projected_qty, 0)) as "Qté Projeté:Float:100", 
#	sum(ifnull(mr_item.max_order_qty, 0)) as "Qté Max d'achat:Float:150", 
#	(sum(mr_item.stock_qty) - sum(ifnull(mr_item.ordered_qty, 0))) as "Qté à commandée:Float:130",
#	mr_item.last_purchase_rate as "Dérnier Prix d'achat::150",
#	it.last_purchase_devise as "Dérnier Prix d'achat (EUR)::170",
#	it.prices as "Prix d'achat::650",
#	it.selling as "Prix de vente::650" 
#	
#from
#	`tabMaterial Request Item` mr_item ,`tabMaterial Request` mr, `tabItem` it   
#where
#	mr_item.parent = mr.name 
#	and it.name = mr_item.item_code
#	and mr.material_request_type = "Purchase"
#	and mr_item.docstatus = 1
#	and mr_item.consulted = 0
#	and mr.status != "Stopped"
#group by mr_item.item_code
#having
#	sum(ifnull(mr_item.ordered_qty, 0)) < sum(ifnull(mr_item.stock_qty, 0))
#order by mr_item.creation asc

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
			"label": _("Qté demandée"),
			"width": 80
		})
	columns.append({
			"fieldname": "qts_reliquat",
			"label": _("Qté reliquats"),
			"width": 80
		})
	columns.append({
			"fieldname": "qts_reliquat_modele",
			"label": _("Qté reliquats Modele"),
			"width": 80
		})
	columns.append({
			"fieldname": "qts_variante_stock",
			"label": _("Qté Variante En Stock"),
			"width": 80
		})
	columns.append({
			"fieldname": "qts_projete",
			"label": _("Qté Projeté"),
			"width": 80
		})
	columns.append({
			"fieldname": "qts_max_achat",
			"label": _("Qté Max d'achat"),
			"width": 80
		})
	columns.append({
			"fieldname": "qts_a_commande",
			"label": "Qté à commandée (demandées - projté)",
			"width": 80
		})
	columns.append({
			"fieldname": "last_purchase_rate",
			"label": "Dérnier Prix d'achat",
			"width": 80
		})
	columns.append({
			"fieldname": "last_purchase_rate",
			"label": "Dérnier Prix d'achat (Devise)",
			"width": 80
		})
	columns.append({
			"fieldname": "last_purchase_rate",
			"label": "Dérnier Prix d'achat (Devise)",
			"width": 80
		})
	
	price_lists= frappe.get_all("Price List",filters={"buying":1},fields=["name"])
	if price_lists:
		for pl in price_lists:
			columns.append({
				"fieldname": pl.name,
				"label": pl.name,
				"width": 80
			})
	
	mris = frappe.get_all("Material Request Item",filters={"docstatus":1,"consulted" : filters.article_consulted}, fields=["name","item_code","item_name"])
	for mri in mris:
		data.append([mri.item_code])
		
	return columns, data
