# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.stock.get_item_details import get_item_details

def execute(filters=None):
	
	columns, data = [], []
	if not filters.consultation and not filters.demande:
		frappe.msgprint("Selectionner une consultation ou une demande de materiel")
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
			"fieldname": "material_request",
			"label": _("Material Request"),
			"fieldtype": "Link",
			"options": "Material Request",
			"width": 150
		})
	columns.append({
			"fieldname": "supplier_quotation",
			"label": _("Consultation"),
			"fieldtype": "Link",
			"options": "Supplier Quotation",
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
			"fieldname": "qts_demande",
			"label": _("Qte Demandee Variante"),
			"width": 150
		})
	columns.append({
			"fieldname": "qts_demande_g",
			"label": _("Total de Qte Demande de materiel"),
			"width": 220
		})
	columns.append({
			"fieldname": "qts_demande_modele",
			"label": _("Qte Demandee Modele"),
			"width": 180
		})
	columns.append({
			"fieldname": "qts_reliquat",
			"label": _("Qte reliquats Variante"),
			"width": 160
		})
	columns.append({
			"fieldname": "qts_reliquat_modele",
			"label": _("Qte reliquats Modele"),
			"width": 150
		})
	columns.append({
			"fieldname": "qts_variante_stock",
			"label": _("Qte Variante En Stock"),
			"width": 150
		})
	columns.append({
			"fieldname": "qts_variante_stock",
			"label": _("Qte Modele En Stock"),
			"width": 150
		})
	columns.append({
			"fieldname": "qts_projete",
			"label": _("Qte Projete Variante"),
			"width": 150
		})
	columns.append({
			"fieldname": "qts_projete_model",
			"label": _("Qte Projete Modele"),
			"width": 150
		})
	columns.append({
			"fieldname": "qts_max_achat",
			"label": _("Qte Max d'achat (Modele)"),
			"width": 150
		})
	columns.append({
			"fieldname": "qts_a_commande",
			"label": "Qte a commandee (demandees - projte)",
			"width": 150
		})
	columns.append({
			"fieldname": "qts_a_commande_modele",
			"label": "Qte a commandee par modele (demandees - projete)",
			"width": 280
		})
	columns.append({
			"fieldname": "last_purchase_rate",
			"label": "Dernier Prix d'achat (DZD)",
			"width": 150
		})
	columns.append({
			"fieldname": "last_purchase_rate",
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
	if filters.demande:
		mris = frappe.get_all("Material Request Item",
				      filters={"ordered_qty":0,"creation":(">=",filters.from_date),"parent":filters.demande,"docstatus":1},
				      fields=["model","qty","last_purchase_rate","max_order_qty","projected_qty","actual_qty","stock_qty","ordered_qty","name","item_code","item_name","parent","consultation","fabricant","ref_fabricant"])
	#if filters.fabricant:
	#	mris = frappe.get_all("Material Request Item",
	#			      filters={"creation":(">=",filters.from_date),"fabricant":filters.fabricant,"docstatus":1,"consulted" : filters.article_consulted},
	#			      fields=["model","qty","last_purchase_rate","max_order_qty","projected_qty","actual_qty","stock_qty","ordered_qty","name","item_code","item_name","parent","consultation","fabricant","ref_fabricant"])
	elif filters.consultation:
		mris = frappe.get_all("Material Request Item",
				      filters={"ordered_qty":0,"creation":(">=",filters.from_date),
					       "consultation":filters.consultation,"docstatus":1}, 
				      fields=["model","qty","last_purchase_rate","max_order_qty","projected_qty","actual_qty","stock_qty","ordered_qty","name","item_code","item_name","parent","consultation","fabricant","ref_fabricant"])
	#else:
	#	mris = frappe.get_all("Material Request Item",
	#			      filters={"ordered_qty":0,"creation":(">=",filters.from_date),"docstatus":1},
	#			      fields=["model","qty","last_purchase_rate","max_order_qty","projected_qty","actual_qty","stock_qty","ordered_qty","name","item_code","item_name","parent","consultation","fabricant","ref_fabricant"])

	for mri in mris:
		last_purchase_devise = frappe.get_value('Item', mri.item_code, 'last_purchase_devise')
		model = frappe.get_value('Item', mri.item_code, 'variant_of')
		bins = get_latest_stock_qty(mri.model)
		ibins = get_item_qty(mri.item_code)
		modele_stock_qty = bins[1]
		modele_ordered_qty = bins[3]
		modele_actual_qty = bins[0]
		modele_proj = bins[2]
		#modele_stock_qty = sum(a.qty for a in mris if a.qty and a.model  and a.model == mri.model)
		#and a.model == mri.model
		#modele_ordered_qty = sum([a.ordered_qty for a in mris if (a.ordered_qty and a.model and a.model == mri.model)])
		qts_a_commande = mri.stock_qty - mri.projected_qty
		#modele_actual_qty = sum([a.actual_qty for a in mris if ( a.actual_qty and a.model and a.model == mri.model)])
		if modele_ordered_qty:
			modele_qts_a_commande =  mri.stock_qty - modele_ordered_qty
		else:
			modele_qts_a_commande = 0
		row = [mri.item_code,
		       mri.item_name,
		       mri.parent,
		       mri.consultation,
		       mri.fabricant,
		       mri.ref_fabricant,
		       mri.qty,
		       ibins[1],
		       modele_stock_qty,
		       ibins[3],
		       modele_ordered_qty,
		       ibins[0],
		       modele_actual_qty,
		       ibins[2],
		       modele_proj,
		       mri.max_order_qty,
		       qts_a_commande,
		       modele_qts_a_commande,
		       mri.last_purchase_rate,
		       last_purchase_devise]
		
		# get prices in each price list
		if price_lists and model:
			for pl in price_lists:
				if pl.name:
					price = frappe.db.sql("""select price_list_rate from `tabItem Price` where buying=1 and price_list=%s and ( item_model=%s or item_code=%s) ORDER BY creation DESC LIMIT 1;""",(pl.name,model,mri.item_code))
					if price:
						row.append(price[0][0])
					else:
						row.append(0)
				else:
					row.append(0)
		
		data.append(row)
		
	return columns, data

def get_latest_stock_qty(model, warehouse=None):
	values, condition = [model], ""
	if warehouse:
		values.append(warehouse)
		condition += " AND warehouse = %s"

	actual_qty = frappe.db.sql("""select sum(actual_qty), sum(indented_qty), sum(projected_qty), sum(ordered_qty) from tabBin
		where model=%s {0}""".format(condition), values)[0]

	return actual_qty

def get_item_qty(model, warehouse=None):
	values, condition = [model], ""
	if warehouse:
		values.append(warehouse)
		condition += " AND warehouse = %s"

	actual_qty = frappe.db.sql("""select sum(actual_qty), sum(indented_qty), sum(projected_qty), sum(ordered_qty) from tabBin
		where item_code=%s {0}""".format(condition), values)[0]

	return actual_qty
