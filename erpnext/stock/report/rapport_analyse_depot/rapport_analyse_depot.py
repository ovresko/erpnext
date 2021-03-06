# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe import _, _dict
from erpnext.stock.get_item_details import get_item_details
from frappe.utils import getdate, cstr, flt, fmt_money

def execute(filters=None):
	columns, data = [], []
	if not filters.get('warehouse'):
		frappe.msgprint("Vous devez inserer un entrepot pour filtrer")
		return columns, data
	
	#if not filters.group and not filters.get("recu") and not filters.ref_fabricant and not filters.item_code and not filters.generation_v and not filters.marque_v and not filters.variant_of and not filters.modele_v and not filters.version and not filters.price_list and not filters.perfection and not filters.manufacturer:
	#	#frappe.msgprint("Appliquer un filtre")
	#	return columns, data
	
	
	if filters.get('manufacturer'):
		manufacturers = cstr(filters.get("manufacturer")).strip()
		filters.manufacturer = [d.strip() for d in manufacturers.split(',') if d]
	if filters.get('manufacturer_lp'):
		manufacturer_lp = cstr(filters.get("manufacturer_lp")).strip()
		filters.manufacturer_lp = [d.strip() for d in manufacturer_lp.split(',') if d]
		
	columns.append({
			"fieldname": "commander",
			"label": "Commander",
			"width": 370
		})
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
			"fieldname": "perfection",
			"label": "Perfection",
			"width": 150
		})
	columns.append({
			"fieldname": "qts_local",
			"label": "Qts Actuel",
			"width": 150
		})
	columns.append({
			"fieldname": "qts_demande",
			"label": "Qts Demande",
			"width": 150
		})
	columns.append({
			"fieldname": "qts_depot",
			"label": "Qts Depot",
			"width": 150
		})
	columns.append({
			"fieldname": "qts_magasin",
			"label": "Qts Magasin",
			"width": 150
		})
	columns.append({
			"fieldname": "qts",
			"label": "Qte Total",
			"width": 150
		})

	#if filters.show_price:
	#	price_lists= frappe.get_all("Price List",filters={"buying":1},fields=["name","currency"])
	#	if price_lists:
	#		columns.append({
	#					"fieldname": "all_prices",
	#					"label": "Prix article",
	#					"width": 450
	#				})
		#	for pl in price_lists:
		#		columns.append({
		#			"fieldname": pl.name,
		#			"label": "%s (%s)" % (pl.name,pl.currency),
		#			"width": 150
		#		})
	mris = []

	order_by_statement = "order by item_code"
	items = []
	qts_min = filters.get('qts_min') or 0
	if filters.get("recu"):
		r = filters.get("recu")
		rec_items = frappe.get_all("Purchase Receipt Item", fields=["item_code"], filters={"parent":r})
		rec_items_str = ", ".join("'%s'" % re.item_code for re in rec_items)
		items = frappe.db.sql(
			"""
			select
				stock_uom,item_bloque, perfection,is_purchase_item,qts_total,qts_depot,weight_per_unit,variant_of,has_variants,item_name, item_code, manufacturer,last_purchase_rate , manufacturer_part_no, item_group,last_purchase_devise,max_order_qty,max_ordered_variante
			from `tabItem`
			where disabled=0 and qts_total is not null and qts_total != "0" and has_variants=0 {conditions} and item_code in ({rec}) and item_code in (select obin.item_code from `tabBin` obin where obin.actual_qty > 0 and obin.item_code = item_code and obin.is_group=0 and obin.warehouse != '{warehouse}') and item_code not in (select bin.item_code from `tabBin` bin where bin.actual_qty > {qts_min} and bin.item_code = item_code and bin.warehouse = '{warehouse}')
			{order_by_statement}
			""".format(
				conditions=get_conditions(filters),
				rec=rec_items_str,
				qts_min = qts_min,
				warehouse = filters.get('warehouse'),
				order_by_statement=order_by_statement
			),
			filters, as_dict=1)
		
	else:
		items = frappe.db.sql(
			"""
			select
				stock_uom,item_bloque, perfection,is_purchase_item,qts_total,qts_depot,weight_per_unit,variant_of,has_variants,item_name, item_code, manufacturer,last_purchase_rate , manufacturer_part_no, item_group,last_purchase_devise,max_order_qty,max_ordered_variante
			from `tabItem`
			where disabled=0 and qts_total is not null and qts_total != "0" and has_variants=0 {conditions} and item_code in (select obin.item_code from `tabBin` obin where obin.actual_qty > 0 and obin.item_code = item_code and obin.is_group=0 and obin.warehouse != '{warehouse}') and item_code not in (select bin.item_code from `tabBin` bin where bin.actual_qty > {qts_min} and bin.item_code = item_code and bin.warehouse = '{warehouse}')
			{order_by_statement}
			""".format(
				conditions=get_conditions(filters),
				qts_min = qts_min,
				warehouse = filters.get('warehouse'),
				order_by_statement=order_by_statement
			),
			filters, as_dict=1)
	all_items = []
	item_dc = {}
	mcomplements = []
	models = []
	_models = {item.variant_of for item in items if item.variant_of}
	models_copy = []
	models_copy.extend(_models)
	ids = {o.item_code for o in items if o.item_code}
	lids = "','".join(ids)
	if filters.get('grouped'):
		for m in models_copy:
			if m in models:
				pass
			else:
				models.insert(len(models),m)
				complements = frappe.get_all("Composant",filters={"parent":m,"parentfield":"articles"},fields=["parent","item"])
				if complements:
					parents = {i.item for i in complements}
					if parents:
						for t in parents:
							_models.discard(t)
							if t in models:
								models.remove(t)
							models.insert(len(models),t)
							mcomplements.append(t)
							comp_items = frappe.db.sql(
									"""
									select
										stock_uom,item_bloque, qts_total,qts_depot,perfection,is_purchase_item,weight_per_unit,variant_of,has_variants,item_name, item_code, manufacturer,last_purchase_rate , manufacturer_part_no, item_group,last_purchase_devise,max_order_qty,max_ordered_variante
									from `tabItem`
									where disabled=0 and has_variants=0  and variant_of=%s and  item_code not in ('{0}')

									""".format(lids),
									(t), as_dict=1)
							#for ci in comp_items:
							#	ci.update({"item_code":"%s CP" % ci.item_code})
							items.extend(comp_items)

		if not models or len(models) <= 0:
			frappe.msgprint("Aucune resultat")
			return columns, data
		ids = {o.item_code for o in items if o.item_code}
		lids = "','".join(ids)
	
		for model in models:

			exitems = frappe.db.sql(
			"""
			select
				stock_uom,item_bloque, perfection,is_purchase_item,weight_per_unit,qts_total,qts_depot,variant_of,has_variants,item_name, item_code, manufacturer,last_purchase_rate , manufacturer_part_no, item_group,last_purchase_devise,max_order_qty,max_ordered_variante
			from `tabItem`
			where disabled=0 and has_variants=0 and variant_of = %s and item_code not in ('{0}')
			""".format(lids),
			(model), as_dict=1)
			items.extend(exitems)

			_mitems = [item for item in items if item.variant_of == model]
			origin_model = frappe.get_doc("Item",model)
			mitems = [origin_model]
			mitems.extend(_mitems)

			for mri in mitems:
				global info
				qts_max_achat = 0
				if mri.variant_of:
					qts_max_achat = mri.max_ordered_variante
				elif mri.has_variants:
					qts_max_achat = mri.max_order_qty
				
				last_qty = 0				
				last_valuation = 0
				recom = 0
				_date = ""
				date =""
				qts_local = 0
				qts_demande = 0
				bin = frappe.db.sql("""select actual_qty from `tabBin` where item_code = %s and warehouse = %s limit 1""", (mri.item_code, filters.get('warehouse')), as_dict=1)
				if bin and len(bin) > 0:
					qts_local = bin[0].actual_qty or 0
					if qts_local < 0:
						qts_local = 0
				qts_demande =  frappe.db.sql("""select sum(mri.qty) sumqty  from `tabMaterial Request Item` mri LEFT JOIN `tabMaterial Request` mr on mri.parent = mr.name where mri.item_code = %s and mri.warehouse = %s and mr.material_request_type='Material Transfer' and mr.docstatus=1 and mr.status!='Stopped' """, (mri.item_code, filters.get('warehouse')), as_dict=1)
				if qts_demande:
					qts_demande = qts_demande[0].sumqty or 0
					if qts_demande < 0:
						qts_demande = 0
				if filters.get('demande') and (qts_local+qts_demande) > qts_min:
					continue
							
					
				cmp = "%s CP" % mri.item_code if (mri.has_variants and mri.item_code in mcomplements) else mri.item_code
				qts_elswhere = flt(mri.qts_depot or 0) - flt(qts_local or 0)				
				if filters.disp_g==1 and qts_elswhere <= 0:
					continue
				row = ["""<input type='button' onclick="erpnext.utils.open_item_info('%s', this)" value='info'>  </input> &nbsp;&nbsp;&nbsp; <button id='%s' onClick="demander_item('%s')" type='button'>Demander</button><input placeholder='Qts' id='input_%s' style='color:black'></input>""" % (mri.item_code,mri.item_code,mri.item_code,mri.item_code),
				       cmp,
				       mri.item_name,
				       mri.stock_uom,
				       mri.manufacturer,
				       mri.manufacturer_part_no,
				       mri.perfection,
				       qts_local,
				       qts_demande,
				       qts_elswhere,
				       flt(mri.qts_total or 0) - flt(mri.qts_depot or 0),
				       mri.qts_total,
				       
				      ]

				data.append(row)
	else:
		for mri in items:
				global info
				qts_max_achat = 0
				if mri.variant_of:
					qts_max_achat = mri.max_ordered_variante
				elif mri.has_variants:
					qts_max_achat = mri.max_order_qty
				
				last_qty = 0
				
				last_valuation = 0
				recom = 0
				_date = ""
				date =""
				qts_local=0
				qts_demande = 0
				bin = frappe.db.sql("""select actual_qty from `tabBin` where item_code = %s and warehouse = %s limit 1""", (mri.item_code, filters.get('warehouse')), as_dict=1)
				if bin and len(bin) > 0:
					qts_local = bin[0].actual_qty or 0
					if qts_local < 0:
						qts_local = 0
				qts_demande =  frappe.db.sql("""select sum(mri.qty) sumqty  from `tabMaterial Request Item` mri LEFT JOIN `tabMaterial Request` mr on mri.parent = mr.name where mri.item_code = %s and mri.warehouse = %s and mr.material_request_type='Material Transfer' and mr.docstatus=1 and mr.status!='Stopped' """, (mri.item_code, filters.get('warehouse')), as_dict=1)
				if qts_demande:
					qts_demande = qts_demande[0].sumqty or 0
					if qts_demande < 0:
						qts_demande = 0
				if filters.get('demande') and (qts_local+qts_demande) > qts_min:
					continue
					
				cmp = "%s CP" % mri.item_code if (mri.has_variants and mri.item_code in mcomplements) else mri.item_code
				qts_elswhere = flt(mri.qts_depot or 0) - flt(qts_local or 0)				
				if filters.disp_g==1 and qts_elswhere <= 0:
					continue
				row = ["""<input type='button' onclick="erpnext.utils.open_item_info('%s', this)" value='info'>  </input> &nbsp;&nbsp;&nbsp; <button id='%s' onClick="demander_item('%s')" type='button'>Demander</button><input placeholder='Qts' id='input_%s' style='color:black'></input>""" % (mri.item_code,mri.item_code,mri.item_code,mri.item_code),
				       cmp,
				       mri.item_name,
				       mri.stock_uom,
				       mri.manufacturer,
				       mri.manufacturer_part_no,
				       mri.perfection,
				       qts_local,
				       qts_demande,
				       qts_elswhere,
				       flt(mri.qts_total or 0) - flt(mri.qts_depot or 0),
				       mri.qts_total,
				       
				      ]

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
	#if filters.get('is_purchase'):	
	#	conditions.append("is_purchase_item=1")
		
	if filters.get('version'):
		nversion = frappe.db.get_value("Version vehicule",filters.get('version'),"version")
		if nversion:
			conditions.append("""(nom_generique_long  LIKE '%%{0}%%')""".format(nversion))
		
	if filters.get('modele_v'):
		nmodele = frappe.db.get_value("Modele de vehicule",filters.get('modele_v'),"modele")
		if nmodele:
			conditions.append("""(nom_generique_long  LIKE '%%{0}%%')""".format(nmodele))	

	if filters.get('marque_v'):
		nmarque = frappe.db.get_value("Marque vehicule",filters.get('marque_v'),"marque")
		if nmarque:
			conditions.append("""(nom_generique_long  LIKE '%%{0}%%')""".format(nmarque))

	if filters.get('generation_v'):
		ngeneration = frappe.db.get_value("Generation vehicule",filters.get('generation_v'),"nom_generation")
		if ngeneration:
			conditions.append("""(nom_generique_long  LIKE '%%{0}%%')""".format(ngeneration))

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
		conditions.append("(variant_of in  (select variant_of  from tabItem where manufacturer_part_no LIKE  '%%{0}%%' or clean_manufacturer_part_number LIKE  '%%{0}%%'))".format(filters.ref_fabricant))
		#conditions.append("(manufacturer_part_no LIKE  '%%{0}%%' or clean_manufacturer_part_number LIKE  '%%{0}%%')".format(filters.ref_fabricant))
	
	if filters.get('item_code'):
		conditions.append("item_code LIKE '%%{0}%%'".format(filters.item_code))
		#conditions.append("(manufacturer=%(manufacturer)s)")
		
	return "and {}".format(" and ".join(conditions)) if conditions else ""

def info_modele(model, warehouse=None):
	values, condition = [model], ""
	if warehouse:
		values.append(warehouse)
		condition += " AND warehouse = %s"

	actual_qty = frappe.db.sql("""select sum(actual_qty), sum(IF(warehouse = "GLOBAL - MV", indented_qty, 0)), sum(IF(warehouse = "GLOBAL - MV", projected_qty, 0)), sum(ordered_qty) from tabBin
		where model=%s {0}""".format(condition), values)[0]

	return actual_qty

def info_variante(model, warehouse=None):
	values, condition = [model], ""
	if warehouse:
		values.append(warehouse)
		condition += " AND warehouse = %s"

	actual_qty = frappe.db.sql("""select sum(actual_qty), sum(IF(warehouse = "GLOBAL - MV", indented_qty, 0)), sum(IF(warehouse = "GLOBAL - MV", projected_qty, 0)), sum(ordered_qty) from tabBin
		where item_code=%s {0}""".format(condition), values)[0]

	return actual_qty
