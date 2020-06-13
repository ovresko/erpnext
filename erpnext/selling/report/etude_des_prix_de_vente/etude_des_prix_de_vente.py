# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext, json
from frappe import _, _dict
from erpnext.stock.get_item_details import get_item_details
from frappe.utils import getdate, cstr, flt, fmt_money

def execute(filters=None):
	columns, data = [], []
	if not filters.group and not filters.receipt and not filters.ref_fabricant and not filters.item_code and not filters.generation_v and not filters.marque_v and not filters.variant_of and not filters.modele_v and not filters.version and not filters.price_list and not filters.manufacturer:
		frappe.msgprint("Appliquer un filtre")
		return columns, data
	if filters.get('manufacturer'):
		manufacturers = cstr(filters.get("manufacturer")).strip()
		filters.manufacturer = [d.strip() for d in manufacturers.split(',') if d]

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
			"fieldname": "receipt",
			"label": "Recu d'achat",
			"width": 150
		})
	columns.append({
			"fieldname": "last_qty",
			"label": "Derniere Qts Achetee",
			"width": 250
		})
	columns.append({
			"fieldname": "qts",
			"label": "Qte En stock",
			"width": 250
		})
	columns.append({
			"fieldname": "qts_projete",
			"label": "Qte Projete",
			"width": 250
		})
	columns.append({
			"fieldname": "last_purchase_rate",
			"label": "Dernier Prix d'achat (DZD)",
			"width": 250
		})
	columns.append({
			"fieldname": "last_purchase_devise",
			"label": "Dernier Prix d'achat (Devise)",
			"width": 250
		})
	columns.append({
			"fieldname": "last_valuation",
			"label": "Derniere taux de valorisation",
			"width": 250
		})
	
	#item_code 
	#item_name 
	#uom 
	#fabricant 
	#ref_fabricant 
	#perfection 
	#receipt 
	#last_qty 
	#qts 
	#qts_projete 
	#last_purchase_rate 
	#last_purchase_devise 
	#last_valuation 
	#benefice

	price_lists = []
	price_lists= frappe.get_all("Price List",filters={"selling":1},fields=["name","currency"])
	if price_lists:
		for pl in price_lists:
			columns.append({
				"fieldname": pl.name,
				"label": "%s (%s)" % (pl.name,pl.currency),
				"width": 420
			})

	mris = []

	order_by_statement = "order by sqi.item_code"
	#parent material_request_item - material_request - qty - variant_of - creation
	items = frappe.db.sql(
		"""
		select sqi.parent,
		sqi.qty,
		sqi.creation,
		it.item_code,
		it.item_name,
		it.stock_uom,
		it.weight_per_unit,
		it.item_group,
		it.variant_of,
		it.perfection,
		it.weight_per_unit,
		it.is_purchase_item,
		it.variant_of,
		it.has_variants,
		it.manufacturer,
		it.last_purchase_rate , 
		it.manufacturer_part_no, 
		it.last_purchase_devise,
		it.max_order_qty,
		it.max_ordered_variante
		from `tabPurchase Receipt Item` sqi left join `tabItem` it
		ON sqi.item_code = it.item_code
		where sqi.parent != "" {conditions}
		{order_by_statement}
		""".format(
			conditions=get_conditions(filters),
			order_by_statement=order_by_statement
		),
		filters, as_dict=1)
	all_items = []
	item_dc = {}
	mitems=[]
	
	models = []
	_models= {item.variant_of for item in items if item.variant_of}
	models_copy = []
	models_copy.extend(_models)
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
						
	if not models or len(models) <= 0:
		frappe.msgprint("Aucune resultat")
		return columns, data
	
	
	
	#models = list(set(models))
	#models.sort()
			
	for model in models:
		_mitems = [item for item in items if item.variant_of == model]
		origin_model = frappe.get_doc("Item",model)

		mitems.append(origin_model)
		mitems.extend(_mitems)
		
		oids = {o.item_code for o in mitems if item.item_code}
		others = frappe.get_all("Item",filters={"variant_of":model,"item_code":("not in",oids)},fields=[
		"variant_of",
		"stock_uom", 
		"perfection",
		"is_purchase_item",
		"weight_per_unit",
		"variant_of",
		"has_variants",
		"item_name", 
		"item_code", 
		"manufacturer",
		"last_purchase_rate" , 
		"manufacturer_part_no", 
		"item_group",
		"last_purchase_devise",
		"max_order_qty",
		"max_ordered_variante"])

		mitems.extend(others)
		
	#item_code 
	#item_name 
	#uom 
	#fabricant 
	#ref_fabricant 
	#perfection 
	#receipt 
	#last_qty 
	#qts 
	#qts_projete 
	#last_purchase_rate 
	#last_purchase_devise 
	#last_valuation 
	#benefice
	
	for mri in mitems:
		receipt = ''
		if hasattr(mri, 'parent') and mri.parent:
			receipt = mri.parent
		global info
		qts_max_achat = 0
		last_qty = 0
		last_valuation = 0
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
		if sqllast_qty:
			last_qty = sqllast_qty[0].actual_qty
			last_valuation = sqllast_qty[0].valuation_rate
			if last_valuation:
				last_valuation = round(last_valuation)


		row = [
			mri.item_code,
			mri.item_name,
			mri.stock_uom,
			mri.manufacturer,
			mri.manufacturer_part_no,
			mri.perfection,
			receipt,
			last_qty,
			info[0] or 0,
			info[2] or 0,
			mri.last_purchase_rate  or 0,
			mri.last_purchase_devise  or 0,
			last_valuation or 0
		]

		
		# get prices in each price list
		if price_lists and not mri.has_variants:
			for pl in price_lists:
				itr = ''
				# [ 20% ] [ 1420 ]    ok
				if pl.name:
					#taux
					_price = ''
					new_taux = 0
					benefice =  frappe.db.sql("""select benefice from `tabPrice List` where selling=1 and name=%s ORDER BY creation DESC LIMIT 1;""",(pl.name))
					price = frappe.db.sql("""select price_list_rate,min_qty from `tabItem Price` where selling=1 and price_list=%s and (  item_code=%s) ORDER BY creation DESC;""",(pl.name,mri.item_code))
					if price:
						for p in price:
							_price += "&nbsp;&nbsp;  +%s/%s  &nbsp;&nbsp;" % (p[1],p[0])
					if benefice:
						benefice = benefice[0][0]
						new_taux = round((1+(float(benefice or 0)/100)) * float(mri.last_purchase_rate or 0))
					
					itr = """[ %s %% ]  	&nbsp;	&nbsp;   %s	&nbsp;	&nbsp;	&nbsp;<input placeholder='Prix %s' id='price_%s_%s' value='%s' style='color:black'></input>&nbsp;<input placeholder='Qts' id='qts_%s_%s' style='color:black;width:60px'></input><a  onClick="set_price_item('%s','%s')" type='a'> OK </a>""" % (benefice,_price,pl.name,mri.item_code,pl.name.replace(" ",""),new_taux,mri.item_code,pl.name.replace(" ",""),pl.name,mri.item_code)
				if itr:
					row.append(itr)
				else:
					row.append("_")

		data.append(row)
		
	return columns, data

					       
def get_conditions(filters):
	conditions = []
	# group, modele, manufacturer, age_plus, age_minus
	if filters.get('group'):
		conditions.append("it.item_group=%(group)s")
	
		
	#receipt
	if filters.get('receipt'):
		conditions.append("""sqi.parent=%(receipt)s""")
	
	#perfection
	if filters.get('perfection'):
		conditions.append("it.perfection=%(perfection)s")
	
	if filters.get('variant_of'):
		conditions.append("(it.item_code=%(variant_of)s or it.variant_of=%(variant_of)s)")


	if filters.get('version'):
		conditions.append("""(it.item_code in (select parent from `tabVersion vehicule item` vv
		where vv.version_vehicule=%(version)s))"""  )

	if filters.get('modele_v'):
		modele = frappe.db.get_value("Modele de vehicule", filters.modele_v, "modele")
		#frappe.get_doc('Modele de vehicule',filters.modele_vehicule)
		if modele:
			query = """(it.item_code in (select parent from `tabVersion vehicule item` vm
		where vm.modele_vehicule='%s'))""" % modele
			conditions.append(query)

	if filters.get('marque_v'):
		conditions.append("""(it.item_code in (select parent from `tabVersion vehicule item` vr 
		where vr.marque_vehicule=%(marque_v)s))""")

	if filters.get('generation_v'):
		#generation_vehicule
		generation = frappe.db.get_value("Generation vehicule", filters.generation_v, "generation")
		if generation:
			conditions.append("""(it.item_code in (select parent from `tabVersion vehicule item` vsr 
		where vsr.generation_vehicule='%s'))""" % generation)

	if filters.get('price_list'):
		conditions.append(""" (it.item_code in 
		(select item_code from `tabItem Price` vpr where vpr.price_list=%(price_list)s) 
		or it.variant_of in (select item_model from `tabItem Price` vpr 
		where vpr.price_list=%(price_list)s))""")

	if filters.get('manufacturer'):
		conditions.append("it.manufacturer in %(manufacturer)s")
	
	if filters.get('ref_fabricant'):
		conditions.append("(it.manufacturer_part_no LIKE  '%%{0}%%' or it.clean_manufacturer_part_number LIKE  '%%{0}%%')".format(filters.ref_fabricant))
	
	if filters.get('item_code'):
		conditions.append("it.item_code LIKE '%%{0}%%'".format(filters.item_code))
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
