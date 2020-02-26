# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe import _, _dict
from erpnext.stock.get_item_details import get_item_details
from frappe.utils import getdate, cstr, flt, fmt_money

def execute(filters=None):
	columns, data = [], []
	if not filters.group and not filters.ref_fabricant and not filters.item_code and not filters.generation_v and not filters.marque_v and not filters.variant_of and not filters.modele_v and not filters.version and not filters.price_list and not filters.perfection and not filters.manufacturer:
		frappe.msgprint("Appliquer un filtre")
		return columns, data
	
	if filters.get('manufacturer'):
		manufacturers = cstr(filters.get("manufacturer")).strip()
		filters.manufacturer = [d.strip() for d in manufacturers.split(',') if d]
	if filters.get('manufacturer_lp'):
		manufacturer_lp = cstr(filters.get("manufacturer_lp")).strip()
		filters.manufacturer_lp = [d.strip() for d in manufacturer_lp.split(',') if d]
		
	columns.append({
			"fieldname": "commander",
			"label": "Commander",
			"width": 300
		})
	columns.append({
			"fieldname": "item_code",
			"label": _("Item Code"),
			"width": 150
		})
	columns.append({
			"fieldname": "date_recom",
			"label": "Derniere Date Commande",
			"width": 150
		})
	columns.append({
			"fieldname": "item_name",
			"label": _("Item Name"),
			"width": 150
		})
	columns.append({
			"fieldname": "uom",
			"label": "Unite Mesure",
			"width": 150
		})
	columns.append({
			"fieldname": "fabricant",
			"label": "Fabricant",
			"width": 150
		})
	columns.append({
			"fieldname": "ref_fabricant",
			"label": "Ref Fabricant",
			"width": 150
		})
	columns.append({
			"fieldname": "poids",
			"label": _("Poids"),
			"width": 150
		})
	columns.append({
			"fieldname": "perfection",
			"label": "Perfection",
			"width": 150
		})
	columns.append({
			"fieldname": "last_qty",
			"label": "Derniere Qts Achetee",
			"width": 150
		})
	columns.append({
			"fieldname": "last_valuation",
			"label": "Derniere taux de valorisation",
			"width": 150
		})
	columns.append({
			"fieldname": "consom",
			"label": "Consommation 1 ans",
			"width": 150
		})
	columns.append({
			"fieldname": "qts_reliquat",
			"label": "Qte reliquats",
			"width": 160
		})
	columns.append({
			"fieldname": "qts_dem",
			"label": "Qte Demande non commande",
			"width": 160
		})
	columns.append({
			"fieldname": "qts",
			"label": "Qte",
			"width": 150
		})
	columns.append({
			"fieldname": "qts_projete",
			"label": "Qte Projete",
			"width": 150
		})
	columns.append({
			"fieldname": "qts_demande",
			"label": "Qte en Demande",
			"width": 150
		})
	columns.append({
			"fieldname": "qts_consulte",
			"label": "Qte en Consultation",
			"width": 150
		})
	columns.append({
			"fieldname": "qts_max_achat",
			"label": "Qte Max d'achat",
			"width": 150
		})
	columns.append({
			"fieldname": "qts_recom",
			"label": "Recommande auto",
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
	if filters.show_price:
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
			stock_uom, perfection,is_purchase_item,weight_per_unit,variant_of,has_variants,item_name, item_code, manufacturer,last_purchase_rate , manufacturer_part_no, item_group,last_purchase_devise,max_order_qty,max_ordered_variante
		from `tabItem`
		where disabled=0 and has_variants=0 {conditions}
		{order_by_statement}
		""".format(
			conditions=get_conditions(filters),
			order_by_statement=order_by_statement
		),
		filters, as_dict=1)
	all_items = []
	item_dc = {}
	models = {item.variant_of for item in items if item.variant_of}
	for model in models:
		_mitems = [item for item in items if item.variant_of == model]
		origin_model = frappe.get_doc("Item",model)
		mitems = [origin_model]
		mitems.extend(_mitems)
		
		for mri in mitems:
			global info
			qts_max_achat = 0
			if mri.variant_of:
				#variante
				info = info_variante(mri.item_code)
				qts_max_achat = mri.max_ordered_variante
			elif mri.has_variants:
				info = info_modele(mri.item_code)
				qts_max_achat = mri.max_order_qty
			sqllast_qty = frappe.db.sql("""select actual_qty,valuation_rate from `tabStock Ledger Entry` 
			where item_code=%s and voucher_type=%s 
			order by posting_date, posting_time limit 1""", (mri.item_code,"Purchase Receipt"), as_dict=1)
			last_qty = 0
			qts_consulte = frappe.db.sql("""select sum(qty) from `tabSupplier Quotation Item` 
			where item_code=%s and docstatus=0""", (mri.item_code))[0][0]
			qts_demande = frappe.db.sql("""select sum(qty) from `tabMaterial Request Item` 
			where item_code=%s and docstatus=1 and consulted=0""", (mri.item_code))[0][0]
			last_valuation = 0
			recom = 0
			_date = ""
			date =""
			_recom = frappe.get_all("Item Reorder",fields=["warehouse_reorder_qty","modified"],filters=[{"parent":mri.item_code},{"warehouse":"GLOBAL - MV"}])
			if _recom:
				recom = _recom[0].warehouse_reorder_qty
				_date = _recom[0].modified
				date = frappe.utils.get_datetime(date).strftime("%d/%m/%Y")
			if sqllast_qty:
				last_qty = sqllast_qty[0].actual_qty
				last_valuation = sqllast_qty[0].valuation_rate
			row = ["""<button id='%s' onClick="demander_item('%s')" type='button'>Demander</button><input placeholder='Qts' id='input_%s' style='color:black'></input><button   onClick="achat_item('%s')" type='button'>ACHAT %s</button>""" % (mri.item_code,mri.item_code,mri.item_code,mri.item_code,mri.is_purchase_item),
			       mri.item_code,
			       #date
			       date,
			       mri.item_name,
			       #uom
			       mri.stock_uom,
			       mri.manufacturer,
			       mri.manufacturer_part_no,
			       #poids
			       mri.weight_per_unit,
			       #perfection
			       mri.perfection,
			       #last_qty
			       last_qty or 0,
			       #last_valuation
			       last_valuation or 0,
			       #consom,
			       "_",
			       #qts_reliquat
			       info[3] or 0,
			       #qts_dem
			       info[1] or 0,
			       #qts
			       info[0] or 0,
			       #qts_projete
			       info[2] or 0,
			       qts_demande or 0,
			       qts_consulte or 0,
			       #qts_max_achat
			       qts_max_achat or 0,
			       #recom
			       recom or 0,
			       #last_purchase_rate
			       mri.last_purchase_rate or 0,
			       #last_purchase_devise
			       mri.last_purchase_devise or 0
			      ]

			if filters.show_price:
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
		
	#perfection
	if filters.get('perfection'):
		conditions.append("perfection=%(perfection)s")
	if filters.get('variant_of'):
		conditions.append("(item_code=%(variant_of)s or variant_of=%(variant_of)s)")
	if filters.get('is_purchase'):	
		conditions.append("is_purchase_item=1")
	if filters.get('version'):
		conditions.append("""(item_code in (select parent from `tabVersion vehicule item` vv
		where vv.version_vehicule=%(version)s))"""  )
	if filters.get('modele_v'):
		modele = frappe.db.get_value("Modele de vehicule", filters.modele_v, "modele")
		#frappe.get_doc('Modele de vehicule',filters.modele_vehicule)
		if modele:
			query = """(item_code in (select parent from `tabVersion vehicule item` vm
		where vm.modele_vehicule='%s'))""" % modele
			conditions.append(query)

	if filters.get('marque_v'):
		conditions.append("""(item_code in (select parent from `tabVersion vehicule item` vr 
		where vr.marque_vehicule=%(marque_v)s))""")

	if filters.get('generation_v'):
		#generation_vehicule
		generation = frappe.db.get_value("Generation vehicule", filters.generation_v, "generation")
		if generation:
			conditions.append("""(item_code in (select parent from `tabVersion vehicule item` vsr 
		where vsr.generation_vehicule='%s'))""" % generation)

	if filters.get('price_list'):
		manufacturer_lp = filters.manufacturer_lp
		req = ")"
		if filters.get('manufacturer_lp'):
			req = " and vpr.fabricant in  %(manufacturer_lp)s )"
		conditions.append(""" (item_code in (select item_code from `tabItem Price` vpr 
		where vpr.price_list=%(price_list)s"""+  (req)+""" or variant_of in (select item_model from `tabItem Price` vpr 
		where vpr.price_list=%(price_list)s """+  (req)+""")""")

	#if filters.get('modele'):
	#	conditions.append("(variant_of=%(modele)s or item_code=%(modele)s)")
	
	if filters.get('manufacturer'):
		conditions.append("manufacturer in %(manufacturer)s")
	
	if filters.get('ref_fabricant'):
		conditions.append("(manufacturer_part_no LIKE  '%%{0}%%' or clean_manufacturer_part_number LIKE  '%%{0}%%')".format(filters.ref_fabricant))
	
	if filters.get('item_code'):
		conditions.append("item_code LIKE '%%{0}%%'".format(filters.item_code))
		#conditions.append("(manufacturer=%(manufacturer)s)")
		
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
