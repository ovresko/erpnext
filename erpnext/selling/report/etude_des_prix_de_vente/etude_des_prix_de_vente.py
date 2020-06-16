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
			"fieldname": "info",
			"label": "Info",
			"width": 100
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
			"fieldname": "last_purchase_devise",
			"label": "Dernier Prix d'achat (Devise)",
			"width": 250
		})
	columns.append({
			"fieldname": "last_purchase_rate",
			"label": "Dernier Prix d'achat (DZD)",
			"width": 250
		})
	columns.append({
			"fieldname": "taux_change",
			"label": "Taux de change",
			"width": 200
		})
	columns.append({
			"fieldname": "charge",
			"label": "Montant Charges",
			"width": 200
		})
	columns.append({
			"fieldname": "last_valuation",
			"label": "Derniere taux de valorisation",
			"width": 250
		})
	columns.append({
			"fieldname": "taux_valuation_ttc",
			"label": "Taux TVA 19% (DZD)",
			"width": 250
		})
	columns.append({
			"fieldname": "last_valuation_ttc",
			"label": "Taux de valorisation TTC",
			"width": 250
		})
	columns.append({
			"fieldname": "pond_valuation",
			"label": "Taux valorisation Moyen",
			"width": 250
		})
	columns.append({
			"fieldname": "pond_valuation_ttc",
			"label": "Taux valorisation Moyen TTC",
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
	price_lists= frappe.get_all("Price List",filters={"selling":1,"enabled":1},fields=["name","currency"])
	if price_lists:
		for pl in price_lists:
			columns.append({
				"fieldname": pl.name,
				"label": "%s (%s)" % (pl.name,pl.currency),
				"width": 450
			})
		columns.append({
			"fieldname": "empty",
			"label": "__",
			"width": 100
		})

	mris = []

	order_by_statement = "order by it.item_code"
	#parent material_request_item - material_request - qty - variant_of - creation
	items = frappe.db.sql(
		"""
		select 
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
		from `tabItem` it 
		where  it.disabled=0 and it.has_variants=0 and it.is_sales_item=1 {conditions}
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
		#if hasattr(mri, 'parent') and mri.parent:
		#	receipt = mri.parent
		global info
		qts_max_achat = 0
		last_qty = 0
		qr_last_qty = frappe.db.sql("""select qty from `tabPurchase Receipt Item` 
		where item_code=%s and qty>0 and docstatus=1
		order by creation desc limit 1""", (mri.item_code), as_dict=1)
		if qr_last_qty:
			last_qty = qr_last_qty[0].qty
		last_valuation = 0
		if mri.variant_of:
			#variante
			info = info_variante(mri.item_code)
			qts_max_achat = mri.max_ordered_variante
		elif mri.has_variants:
			info = info_modele(mri.item_code)
			qts_max_achat = mri.max_order_qty
		sqllast_qty = frappe.db.sql("""select incoming_rate,actual_qty,valuation_rate,voucher_type, voucher_no from `tabStock Ledger Entry` 
		where item_code=%s and actual_qty>0 
		order by posting_date desc, posting_time desc limit 1""", (mri.item_code), as_dict=1)
		
		pondere = 0
		if sqllast_qty:
			receipt = "%s %s" % (sqllast_qty[0].voucher_type, sqllast_qty[0].voucher_no)
			
			last_valuation = sqllast_qty[0].incoming_rate
			pondere = sqllast_qty[0].valuation_rate
			if last_valuation:
				last_valuation = round(last_valuation)
		taux_change = 0
		if mri.last_purchase_devise and mri.last_purchase_rate:
			taux_change = mri.last_purchase_rate / mri.last_purchase_devise
		
		charge = 0
		if mri.last_purchase_rate and last_valuation:
			charge = round(last_valuation - mri.last_purchase_rate)
		val_ttc = 0
		taux_taxe =0 
		pond_valuation_ttc=0
		if last_valuation:
			taux_taxe = last_valuation*0.19
			val_ttc = round(last_valuation+taux_taxe)
		pond_valuation = 0
		
		#frappe.db.sql("""select (medium / total) as result from (select t.item_code, sum(t.actual_qty) AS total, (t.actual_qty * t.valuation_rate) AS medium from `tabStock Ledger Entry` t where item_code=%s and actual_qty>0 GROUP BY t.item_code ) as inner_query""", (mri.item_code), as_dict=1)
		if pondere:
			pond_valuation = round(pondere or 0)
			pond_valuation_ttc = round(pond_valuation*1.19)


		row = [
			mri.item_code,
			"""<button   onClick="open_item_info('%s')" type='b'> info </button> &nbsp;&nbsp;&nbsp;""" % (mri.item_code),
			mri.item_name,
			mri.stock_uom,
			mri.manufacturer,
			mri.manufacturer_part_no,
			mri.perfection,
			receipt,
			last_qty,
			info[0] or 0,
			info[2] or 0,
			mri.last_purchase_devise  or 0,
			mri.last_purchase_rate  or 0,	
			taux_change or 0,
			charge or 0,
			last_valuation or 0,
			taux_taxe or 0,
			val_ttc or 0,
			pond_valuation or 0,
			pond_valuation_ttc or 0			
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
							lp_benefice = round(p[0] - val_ttc)
							if val_ttc:
								lp_benefice = round((lp_benefice * 100) / val_ttc) or 0
							_price += "&nbsp;&nbsp;  +%s/%s/%s%%  &nbsp;&nbsp;" % (p[1],p[0],lp_benefice)
					if benefice:
						benefice = benefice[0][0]
						new_taux = round((1+(float(benefice or 0)/100)) * float(val_ttc or 0))
					
					itr = """[ %s %% ]&nbsp;&nbsp;<input placeholder='Prix %s' id='price_%s_%s' value='%s' style='color:black'></input>&nbsp;<input placeholder='Qts' id='qts_%s_%s' style='color:black;width:60px'></input><a  onClick="set_price_item('%s','%s')" type='a'  id='btn_%s_%s'> OK </a>&nbsp;	&nbsp;   %s	""" % (benefice,pl.name,mri.item_code,pl.name.replace(" ",""),new_taux,mri.item_code,pl.name.replace(" ",""),pl.name,mri.item_code,mri.item_code,pl.name.replace(" ",""),_price)
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
		conditions.append(""" it.item_code in (select item_code from `tabPurchase Receipt Item` sqi where sqi.parent=%(receipt)s)""")
	
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
