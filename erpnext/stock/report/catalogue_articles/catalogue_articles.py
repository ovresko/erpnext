# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext, json
from frappe import _, _dict
from erpnext.stock.get_item_details import get_item_details
from frappe.utils import getdate, cstr, flt, fmt_money,cint
from erpnext.stock.doctype.item.item import print_catalogue
from frappe.utils.pdf import get_pdf
import pdfkit	
import os
import json


def execute(filters=None):
	columns, data = [], []
	if not filters.group and not filters.get("recu") and not filters.ref_fabricant and not filters.item_code and not filters.generation_v and not filters.marque_v and not filters.variant_of and not filters.modele_v and not filters.version and not filters.price_list and not filters.perfection and not filters.manufacturer:
		frappe.msgprint("appliquer un filtre plus specifique !")
		return columns, data
	
	if filters.get('manufacturer'):
		manufacturers = cstr(filters.get("manufacturer")).strip()
		filters.manufacturer = [d.strip() for d in manufacturers.split(',') if d]
	if filters.get('price_list'):
		price_list = cstr(filters.get("price_list")).strip()
		filters.price_list = [d.strip() for d in price_list.split(',') if d]
	if filters.get('manufacturer_lp'):
		manufacturer_lp = cstr(filters.get("manufacturer_lp")).strip()
		filters.manufacturer_lp = [d.strip() for d in manufacturer_lp.split(',') if d]
	# marque, desg, code, nom art, oem, fabricant, ref fab, qts depot, qts mag, qts tot, prix...

	if not frappe.has_permission("Email Account", "delete"):
		filters.set('hide_qty',True)
		
	columns.append({
			"fieldname": "info",
			"label": "Info",
			"width": 50
		})
	columns.append({
			"fieldname": "item_code",
			"label": _("Item Code"),
			"width": 150
		})
	columns.append({
			"fieldname": "item_name",
			"label": _("Item Name"),
			"width": 250
		})
	columns.append({
			"fieldname": "marque",
			"label": "Marque",
			"width": 150
		})
	columns.append({
			"fieldname": "pub_name",
			"label": "Generations",
			"width": 350
		})
	
	columns.append({
			"fieldname": "oem",
			"label": "OEM",
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
	if not filters.get('hide_qty'):
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
				"fieldname": "qts_total",
				"label": "Qts Total",
				"width": 150
			})
	columns.append({
				"fieldname": "fiche_infor_link",
				"label": "Lien fiche info.",
				"width": 150
			})

	price_lists = []
	if not filters.get('hide_prices'):
		price_lists= frappe.get_all("Price List",filters={"selling":1,"enabled":1,"buying":0},fields=["name","currency"])
		if price_lists:
			for pl in price_lists:
				if filters.price_list and pl.name not in filters.price_list:
					continue
				columns.append({
					"fieldname": pl.name,
					"label": "%s (%s)" % (pl.name,pl.currency),
					"width": 150
				})
	
	
	mris = []

	order_by_statement = "order by item_code"
	items = []
	if filters.get("recu"):
		r = filters.get("recu")
		rec_items = frappe.get_all("Purchase Receipt Item", fields=["item_code"], filters={"parent":r})
		rec_items_str = ", ".join("'%s'" % re.item_code for re in rec_items)
		items = frappe.db.sql(
			"""
			select
				stock_uom,item_bloque,oem_text,qts_total,qts_depot, perfection,is_purchase_item,weight_per_unit,variant_of,has_variants,item_name, item_code, manufacturer,last_purchase_rate , manufacturer_part_no, item_group,last_purchase_devise,max_order_qty,max_ordered_variante
			from `tabItem`
			where disabled=0 and has_variants=0 {conditions} and item_code in ({rec})
			{order_by_statement}
			""".format(
				conditions=get_conditions(filters),
				rec=rec_items_str,
				order_by_statement=order_by_statement
			),
			filters, as_dict=1)
		
	else:
		items = frappe.db.sql(
			"""
			select
				stock_uom,item_bloque,oem_text, perfection,qts_total,qts_depot,is_purchase_item,weight_per_unit,variant_of,has_variants,item_name, item_code, manufacturer,last_purchase_rate , manufacturer_part_no, item_group,last_purchase_devise,max_order_qty,max_ordered_variante
			from `tabItem`
			where disabled=0 and has_variants=0 {conditions}
			{order_by_statement}
			""".format(
				conditions=get_conditions(filters),
				order_by_statement=order_by_statement
			),
			filters, as_dict=1)
	if filters.get('regroupe'):
		all_items = []
		item_dc = {}
		mcomplements = []
		models = []
		_models = {item.variant_of for item in items if item.variant_of}
		models_copy = []
		models_copy.extend(_models)
		ids = {o.item_code for o in items if o.item_code}
		lids = "','".join(ids)
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
										stock_uom,oem_text,item_bloque,qts_total,qts_depot, perfection,is_purchase_item,weight_per_unit,variant_of,has_variants,item_name, item_code, manufacturer,last_purchase_rate , manufacturer_part_no, item_group,last_purchase_devise,max_order_qty,max_ordered_variante
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
			#if filters.get('model_status') and filters.get('model_status') == "Modele en repture":
			#	projected = info_modele(model)[2] or 0
			#	if projected or projected > 0:
			#		continue
			exitems = frappe.db.sql(
			"""
			select
				stock_uom,item_bloque,oem_text, perfection,is_purchase_item,qts_total,qts_depot,weight_per_unit,variant_of,has_variants,item_name, item_code, manufacturer,last_purchase_rate , manufacturer_part_no, item_group,last_purchase_devise,max_order_qty,max_ordered_variante
			from `tabItem`
			where disabled=0 and has_variants=0 and variant_of = %s and item_code not in ('{0}')
			""".format(lids),
			(model), as_dict=1)
			items.extend(exitems)

			_mitems = [item for item in items if item.variant_of == model]
			origin_model = frappe.get_doc("Item",model)
			mitems = [origin_model]
			mitems.extend(_mitems)
			desg = ""
			vmarque = ""
			if not len(mitems) or len(mitems) == 1:
				continue
			for mri in mitems:				
				global info
				qts_max_achat = 0
				last_valuation = 0
				recom = 0
				_date = ""
				date =""


				if mri.has_variants:
					desg = ""
					vmarque = ""
					#Version vehicule item
					desg_version = frappe.db.sql("""select GROUP_CONCAT(distinct(marque_vehicule)  SEPARATOR ' - ') as marque, GROUP_CONCAT(distinct CONCAT(IFNULL(modele_vehicule,''),' ',IFNULL( generation_vehicule,'')) SEPARATOR ' - ') as name from `tabVersion vehicule item` where  parent='%s' ;""" % (mri.item_code), as_dict=1)
					desg_generation = frappe.db.sql("""select GROUP_CONCAT(distinct(nom_marque)  SEPARATOR ' - ') as marque, GROUP_CONCAT(distinct IFNULL(nom_generation,'') SEPARATOR ' - ') as name from `tabGeneration vehicule item` where  parent='%s' ;""" % (mri.item_code), as_dict=1)
					desg_modele = frappe.db.sql("""select GROUP_CONCAT(distinct(nom_marque)  SEPARATOR ' - ') as marque, GROUP_CONCAT(distinct CONCAT(IFNULL(nom_marque,''),' ',IFNULL(nom_modele,'')) SEPARATOR ' - ') as name from `tabModele vehicule item` where  parent='%s' ;""" % (mri.item_code), as_dict=1)
					desg_marque = frappe.db.sql("""select GROUP_CONCAT(distinct IFNULL(marque,'') SEPARATOR ' - ') as name from `tabMarque vehicule item` where  parent='%s' ;""" % (mri.item_code), as_dict=1)

					dmarques  = [desg_marque[0].name ,desg_modele[0].marque , desg_generation[0].marque,desg_version[0].marque ]
					dmarques = [x for x in dmarques if x]
					vmarque = " - ".join(dmarques)

					#frappe.msgprint("data: %s" % desg_version.name)
					generique = [desg_marque[0].name ,desg_modele[0].name , desg_generation[0].name ,desg_version[0].name ]
					generique =[x for x in generique if x]
					desg = " - ".join(generique)


				cmp = "%s CP *********** " % mri.item_code if (mri.has_variants and mri.item_code in mcomplements) else "%s *********** " % mri.item_code if mri.has_variants else mri.item_code
				qts_magasin = cint(mri.qts_total or 0) - cint(mri.qts_depot or 0)
				lien = """<a href="http://41.220.144.37/result?p=%s" target="_blank" > http://41.220.144.37/result?p=%s </a>""" % (mri.item_code,mri.item_code)
				# marque, desg, code, nom art, oem, fabricant, ref fab, qts depot, qts mag, qts tot, prix...
				if not filters.get('hide_qty'):
					row = ["""<input type='button' onclick="erpnext.utils.open_item_info('%s', this)" value='info'>  </input>""" % mri.item_code,
					       cmp,
					       mri.item_name,
					       vmarque,
					       desg,				       
					       mri.oem_text or '',
					       mri.manufacturer,
					       mri.manufacturer_part_no,
					       mri.qts_depot,
					       qts_magasin,
					       mri.qts_total,
					       lien
					      ]
				else:
					row = ["""<input type='button' onclick="erpnext.utils.open_item_info('%s', this)" value='info'>  </input>""" % mri.item_code,
					       cmp,
					       mri.item_name,
					       vmarque,
					       desg,				       
					       mri.oem_text or '',
					       mri.manufacturer,
					       mri.manufacturer_part_no,
					       lien
					      ]

				# get prices in each price list
				has_atleast_price = 0
				if price_lists and not filters.get('hide_prices'):
					all_prices = ""
					for pl in price_lists:
						if filters.price_list and pl.name not in filters.price_list:
							continue
						if pl.name and not mri.has_variants:						
							price = frappe.db.sql("""select price_list_rate from `tabItem Price` where  price_list=%s and (  item_code=%s) ORDER BY min_qty ASC LIMIT 1;""",(pl.name,mri.item_code))
							if price:
								all_prices = "%.2f" % (price[0][0] or 0)
								row.append(all_prices)
								has_atleast_price = 1
								#row.append(price[0][0])
							else:
								row.append("_")
						else:
							row.append("_")
				if filters.get('has_price') and not has_atleast_price and not mri.has_variants and not filters.hide_prices:
					continue

				if filters.get('manufacturer') and filters.get('only_fabricant')  and mri.manufacturer not in filters.get('manufacturer'):
					continue

				data.append(row)
	else:
		desg = ""
		vmarque = ""
		for mri in items:
			global info
			qts_max_achat = 0
			last_valuation = 0
			recom = 0
			_date = ""
			date =""

			desg = ""
			vmarque = ""
			#Version vehicule item
			desg_version = frappe.db.sql("""select GROUP_CONCAT(distinct(marque_vehicule)  SEPARATOR ' - ') as marque, GROUP_CONCAT(distinct CONCAT(IFNULL(modele_vehicule,''),' ',IFNULL( generation_vehicule,'')) SEPARATOR ' - ') as name from `tabVersion vehicule item` where  parent='%s' ;""" % (mri.item_code), as_dict=1)
			desg_generation = frappe.db.sql("""select GROUP_CONCAT(distinct(nom_marque)  SEPARATOR ' - ') as marque, GROUP_CONCAT(distinct IFNULL(nom_generation,'') SEPARATOR ' - ') as name from `tabGeneration vehicule item` where  parent='%s' ;""" % (mri.item_code), as_dict=1)
			desg_modele = frappe.db.sql("""select GROUP_CONCAT(distinct(nom_marque)  SEPARATOR ' - ') as marque, GROUP_CONCAT(distinct CONCAT(IFNULL(nom_marque,''),' ',IFNULL(nom_modele,'')) SEPARATOR ' - ') as name from `tabModele vehicule item` where  parent='%s' ;""" % (mri.item_code), as_dict=1)
			desg_marque = frappe.db.sql("""select GROUP_CONCAT(distinct IFNULL(marque,'') SEPARATOR ' - ') as name from `tabMarque vehicule item` where  parent='%s' ;""" % (mri.item_code), as_dict=1)


			dmarques  = [desg_marque[0].name ,desg_modele[0].marque , desg_generation[0].marque,desg_version[0].marque ]
			dmarques = [x for x in dmarques if x]
			vmarque = " - ".join(dmarques)

			#frappe.msgprint("data: %s" % desg_version.name)
			generique = [desg_marque[0].name ,desg_modele[0].name , desg_generation[0].name ,desg_version[0].name ]
			generique =[x for x in generique if x]
			desg = " - ".join(generique)


			cmp =mri.item_code
			
			qts_magasin = cint(mri.qts_total or 0) - cint(mri.qts_depot or 0)
			lien = """<a href="http://41.220.144.37/result?p=%s" target="_blank" > http://41.220.144.37/result?p=%s </a>""" % (mri.item_code,mri.item_code)
			# marque, desg, code, nom art, oem, fabricant, ref fab, qts depot, qts mag, qts tot, prix...
			if not filters.get('hide_qty'):
				row = ["""<input type='button' onclick="erpnext.utils.open_item_info('%s', this)" value='info'>  </input>""" % mri.item_code,
				       cmp,
				       mri.item_name,
				       vmarque,
				       desg,			       
				       mri.oem_text or '',
				       mri.manufacturer,
				       mri.manufacturer_part_no,
				       mri.qts_depot,
				       qts_magasin,
				       mri.qts_total,
				       lien
				      ]
			else:
				row = ["""<input type='button' onclick="erpnext.utils.open_item_info('%s', this)" value='info'>  </input>""" % mri.item_code,
				       cmp,
				       mri.item_name,
				       vmarque,
				       desg,			       
				       mri.oem_text or '',
				       mri.manufacturer,
				       mri.manufacturer_part_no,
				       lien
				      ]

			# get prices in each price list
			has_atleast_price = 0
			if price_lists and  not filters.get('hide_prices'):
				all_prices = ""
				for pl in price_lists:
					if filters.price_list and pl.name not in filters.price_list:
						continue
					if pl.name and not mri.has_variants:						
						price = frappe.db.sql("""select price_list_rate from `tabItem Price` where  price_list=%s and (  item_code=%s) ORDER BY min_qty ASC LIMIT 1;""",(pl.name,mri.item_code))
						if price:
							all_prices = "%.2f " % (price[0][0] or 0)
							row.append(all_prices)
							has_atleast_price = 1
							#row.append(price[0][0])
						else:
							row.append("_")
					else:
						row.append("_")
			if filters.get('has_price') and not has_atleast_price and not mri.has_variants and not filters.hide_prices:
				continue

			if filters.get('manufacturer') and filters.get('only_fabricant')  and mri.manufacturer not in filters.get('manufacturer'):
				continue

			data.append(row)
	if filters.get('generate_pdf') and data:
		names = [a[1].replace("*","").replace(" ","").replace("CP","") for a in data]
		final_html = prepare_bulk_print_html(names)
		frappe.msgprint(final_html)
		
	
	return columns, data

def prepare_bulk_print_html(names):
	html = ""
	sc_list = []
	
	data = {}
	items = []
	
	# get items
	for name in names:
		#frappe.msgprint(name)
		items.append(frappe.get_doc("Item", name))
	
	fabricants = {o.manufacturer for o in items if not o.has_variants}
	models = {item.variant_of for item in items if item.variant_of}
	index = 1
	total = len(models)
	for model in models:
		_model = frappe.get_doc("Item", model)
		_variants = [item for item in items if item.variant_of == model]
		versions_all = sum(x.important == True for x in _model.versions)
		gen_all = sum(x.important == True for x in _model.generation_vehicule_supporte)
		oem_all = sum(x.important == True for x in _model.oem)
		critere_piece_all = sum(x.important == True for x in _model.critere_piece)
		data[model] = {"model":_model,"variants":_variants,"total":total,"index":index,"gen_all":gen_all,"versions_all":versions_all,"oem_all":oem_all,"critere_piece_all":critere_piece_all }
		index= index+1
	html_params = { "data": data }
	final_html = frappe.render_template("erpnext/templates/includes/catalog_bulk_print.html", html_params)

	return final_html

def dignity_get_pdf(html, options=None):
	fname = os.path.join("/tmp", "dignity-sc-list-{0}.pdf".format(frappe.generate_hash()))

	try:
		pdfkit.from_string(html, fname, options=options or {})

		with open(fname, "rb") as fileobj:
			filedata = fileobj.read()

	except IOError, e:
		if ("ContentNotFoundError" in e.message
			or "ContentOperationNotPermittedError" in e.message
			or "UnknownContentError" in e.message
			or "RemoteHostClosedError" in e.message):

			# allow pdfs with missing images if file got created
			if os.path.exists(fname):
				with open(fname, "rb") as fileobj:
					filedata = fileobj.read()

			else:
				frappe.throw(_("PDF generation failed because of broken image links"))
		else:
			raise

	finally:
		cleanup(fname)


	return filedata

def cleanup(fname):
	if os.path.exists(fname):
		os.remove(fname)
def get_conditions(filters):
	conditions = []
	# group, modele, manufacturer, age_plus, age_minus
	if filters.get('group'):
		conditions.append("item_group=%(group)s")
	#has_price
	#if filters.get('has_price'):
	#	conditions.append("0 < (select count(ip.item_code) as ct from `tabItem Price` ip where ip.item_code=item_code and ip.buying=0 and ip.selling=1) ")
		
	#perfection
	if filters.get('perfection'):
		conditions.append("perfection=%(perfection)s")
	if filters.get('depot_qty'):
		conditions.append("qts_depot>0")
	if filters.get('magasin_qty'):
		conditions.append("qts_total > 0 and (ifnull(qts_total,0)-ifnull(qts_depot,0))>0")
	
	if filters.get('variant_of'):
		conditions.append("(item_code=%(variant_of)s or variant_of=%(variant_of)s)")
	#if filters.get('is_purchase'):	
	#	conditions.append("is_purchase_item=1")
	if filters.get('version'):
		nversion = frappe.db.get_value("Version vehicule",filters.get('version'),"version")
		if nversion:
			conditions.append("""(nom_generique_long  LIKE '%% {0} %%')""".format(nversion))
		
	if filters.get('modele_v'):
		nmodele = frappe.db.get_value("Modele de vehicule",filters.get('modele_v'),"modele")
		if nmodele:
			conditions.append("""(nom_generique_long  LIKE '%% {0} %%')""".format(nmodele))	

	if filters.get('marque_v'):
		nmarque = frappe.db.get_value("Marque vehicule",filters.get('marque_v'),"marque")
		if nmarque:
			conditions.append("""(nom_generique_long  LIKE '%% {0} %%')""".format(nmarque))

	if filters.get('generation_v'):
		ngeneration = frappe.db.get_value("Generation vehicule",filters.get('generation_v'),"nom_generation")
		if ngeneration:
			conditions.append("""(nom_generique_long  LIKE '%% {0} %%')""".format(ngeneration))

	if filters.get('price_list'):
		manufacturer_lp = filters.manufacturer_lp
		req = ")"
		if filters.get('manufacturer_lp'):
			req = " and vpr.fabricant in  %(manufacturer_lp)s )"
		conditions.append(""" (item_code in (select item_code from `tabItem Price` vpr 
		where vpr.price_list in %(price_list)s"""+  (req)+""" or variant_of in (select item_model from `tabItem Price` vpr 
		where vpr.price_list in %(price_list)s """+  (req)+""")""")

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
