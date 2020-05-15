# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, json
from frappe.utils.nestedset import get_root_of
from frappe.utils import cint
from erpnext.accounts.doctype.pos_profile.pos_profile import get_item_groups

from six import string_types


@frappe.whitelist()
def get_stock_details(item_code):
	magasin = frappe.db.get_single_value("Stock Settings", "entrepot_magasin")
	depot = frappe.db.get_single_value("Stock Settings", "entrepot_depot")
	magasins = frappe.get_all("Warehouse",filters={"parent_warehouse":magasin},fields=["name"])
	depots = frappe.get_all("Warehouse",filters={"parent_warehouse":depot},fields=["name"])
	magasins_names = ','.join((x.name for x in magasins))
	depots_names = ','.join((x.name for x in depots))
	res_magasins = frappe.db.sql(""" select sum(actual_qty) from `tabBin` where item_code='{}' and warehouse in ('{}') """.format(item_code,magasins_names), as_dict=1)
	res_depots = frappe.db.sql(""" select sum(actual_qty) from `tabBin` where item_code='{}' and warehouse in ('{}') """.format(item_code,depots_names), as_dict=1)
	return res_magasins[0],res_depots[0]

@frappe.whitelist()
def make_devis(customer,items):
	#frappe.msgprint(items)
	items = json.loads(items)
	
	so = frappe.new_doc("Quotation")
	so.customer = customer
	so.party_name = customer
	for item in items:
		item = frappe._dict(item)
		item.doctype="Quotation Item"
		item.parent=so.name
		item.parenttype = "Quotation"
		
		so.append('items', item)
	
	so.save()
	return so

@frappe.whitelist()
def make_sales_order(customer,items):
	#frappe.msgprint(items)
	items = json.loads(items)
	
	so = frappe.new_doc("Sales Order")
	so.customer = customer
	for item in items:
		item = frappe._dict(item)
		item.doctype="Sales Order Item"
		item.parent=so.name
		item.parenttype = "Sales Order"
		
		so.append('items', item)
	
	so.save()
	return so

@frappe.whitelist()
def get_items(start, page_length, price_list, item_group, search_value="", pos_profile=None,item_manufacturer=None,item_modele=None, vehicule_marque=None, vehicule_modele=None, vehicule_generation=None, vehicule_version=None):
	data = dict()
	warehouse = ""
	display_items_in_stock = 0

	if pos_profile:
		warehouse, display_items_in_stock = frappe.db.get_value('POS Profile', pos_profile, ['warehouse', 'display_items_in_stock'])

	if not frappe.db.exists('Item Group', item_group):
		item_group = get_root_of('Item Group')

	if search_value:
		data = search_serial_or_batch_or_barcode_number(search_value)

	item_code = data.get("item_code") if data.get("item_code") else search_value
	serial_no = data.get("serial_no") if data.get("serial_no") else ""
	batch_no = data.get("batch_no") if data.get("batch_no") else ""
	barcode = data.get("barcode") if data.get("barcode") else ""
	#item_manufacturer = data.get("item_manufacturer") if data.get("item_manufacturer") else ""

	item_code, condition = get_conditions(item_code, serial_no, batch_no, barcode)

	if pos_profile:
		condition += get_item_group_condition(pos_profile)

	if item_modele:
		condition += get_item_modele(item_modele)

	if item_manufacturer:
		condition += get_item_manufacturer(item_manufacturer)

	if vehicule_version:
		condition += get_item_version(vehicule_version)
	elif vehicule_generation:
		condition += get_item_generation(vehicule_generation)
	elif vehicule_modele:
		condition += get_vehicule_modele(vehicule_modele)
	elif vehicule_marque:
		condition += get_item_marque(vehicule_marque)
	

	lft, rgt = frappe.db.get_value('Item Group', item_group, ['lft', 'rgt'])
	# locate function is used to sort by closest match from the beginning of the value


	if display_items_in_stock == 0:
		res = frappe.db.sql("""select i.name as item_code,item_adr.adresse,item_adr.warehouse,i.designation_commerciale,i.variant_of,i.has_variants, i.item_name, i.image as item_image, i.idx as idx,i.clean_manufacturer_part_number, i.composant_text,i.articles_text,
			i.is_stock_item, item_det.price_list_rate, item_det.currency, i.oem_text,i.titre_article,i.manufacturer,i.manufacturer_part_no,i.fabricant_logo,i.critere_text ,item_bin.actual_qty
			from `tabItem` i LEFT JOIN (select item_code, price_list_rate, currency from
					`tabItem Price`	where price_list=%(price_list)s) item_det
			ON
				(item_det.item_code=i.name or item_det.item_code=i.variant_of)
			LEFT JOIN (select item_code, actual_qty, warehouse from
					`tabBin` where warehouse=%(warehouse)s) item_bin
			ON
				(item_bin.item_code=i.name or item_bin.item_code=i.variant_of) 
			LEFT JOIN (select parent, warehouse, adresse from `tabAdresse Magasin`) item_adr
			ON
				(item_adr.parent=i.name and  item_adr.warehouse=%(warehouse)s) 
			where 
				i.disabled = 0 and i.has_variants = 0 and i.is_sales_item = 1
				and i.item_group in (select name from `tabItem Group` where lft >= {lft} and rgt <= {rgt})
		        	and {condition}  limit {start}, {page_length}""".format(start=start,page_length=page_length,lft=lft, rgt=rgt,condition=condition),
			{
				'item_code': item_code,
				'price_list': price_list,
				'warehouse':warehouse
			} , as_dict=1)

		res = {
		'items': res
		}

	elif display_items_in_stock == 1:
		query = """select i.name as item_code,i.variant_of,item_adr.adresse,item_adr.warehouse,i.designation_commerciale,i.has_variants, i.item_name, i.image as item_image, i.idx as idx,i.clean_manufacturer_part_number,i.composant_text,i.articles_text,
				i.is_stock_item, item_det.price_list_rate, item_det.currency, i.oem_text,i.titre_article,i.manufacturer,i.manufacturer_part_no,i.fabricant_logo , i.critere_text  
				from `tabItem` i LEFT JOIN
					(select item_code, price_list_rate, currency from
						`tabItem Price`	where price_list=%(price_list)s) item_det
				ON
					(item_det.item_code=i.name or item_det.item_code=i.variant_of) INNER JOIN
				
					"""

		if warehouse is not None:
			query = query +  """ (select item_code,actual_qty from `tabBin` where warehouse=%(warehouse)s and actual_qty > 0 group by item_code) item_se"""
		else:
			query = query +  """ (select item_code,sum(actual_qty) as actual_qty from `tabBin` group by item_code) item_se"""

		res = frappe.db.sql(query +  """
			ON
				((item_se.item_code=i.name or item_det.item_code=i.variant_of) and item_se.actual_qty>0)
			LEFT JOIN (select parent, warehouse, adresse from `tabAdresse Magasin`) item_adr
			ON
				(item_adr.parent=i.name and  item_adr.warehouse=%(warehouse)s) 
			where
				i.disabled = 0 and i.has_variants = 0 and i.is_sales_item = 1
				and i.item_group in (select name from `tabItem Group` where lft >= {lft} and rgt <= {rgt})
				and {condition}  limit {start}, {page_length}""".format(start=start,page_length=page_length,lft=lft, 	rgt=rgt, condition=condition),
			{
				'item_code': item_code,
				'price_list': price_list,
				'warehouse': warehouse
			} , as_dict=1)

		res = {
		'items': res
		}

	if serial_no:
		res.update({
			'serial_no': serial_no
		})

	if batch_no:
		res.update({
			'batch_no': batch_no
		})

	if barcode:
		res.update({
			'barcode': barcode
		})

	return res

@frappe.whitelist()
def search_serial_or_batch_or_barcode_number(search_value):
	# search barcode no
	barcode_data = frappe.db.get_value('Item Barcode', {'barcode': search_value}, ['barcode', 'parent as item_code'], as_dict=True)
	if barcode_data:
		return barcode_data

	# search serial no
	serial_no_data = frappe.db.get_value('Serial No', search_value, ['name as serial_no', 'item_code'], as_dict=True)
	if serial_no_data:
		return serial_no_data

	# search batch no
	batch_no_data = frappe.db.get_value('Batch', search_value, ['name as batch_no', 'item as item_code'], as_dict=True)
	if batch_no_data:
		return batch_no_data

	return {}

def get_conditions(item_code, serial_no, batch_no, barcode):
	if serial_no or batch_no or barcode:
		return frappe.db.escape(item_code), "i.name = %(item_code)s"
	if not item_code:
		return ""," 1=1 "
	words = item_code.split()
	keyword = '* '.join(w for w in words)

	#condition = """ ( i.clean_manufacturer_part_number LIKE '%%{}%%' or i.oem_text LIKE '%%{}%%' or  MATCH(i.name,i.item_name,i.nom_generique_long,i.manufacturer_part_no,i.clean_manufacturer_part_number,i.oem_text) AGAINST('({})' IN NATURAL LANGUAGE MODE)  )""".format(item_code,item_code,item_code)
	condition = """ (  i.clean_manufacturer_part_number LIKE '%%{}%%' or  i.manufacturer_part_no LIKE '%%{}%%' or i.oem_text LIKE '%%{}%%' or MATCH(i.nom_generique_long) AGAINST('({}) ({})' IN NATURAL LANGUAGE MODE)  )""".format(item_code,item_code,item_code,keyword,item_code)

	return '%%%s%%'%(frappe.db.escape(item_code)), condition

def get_item_modele(item_modele):
	cond = """ and i.variant_of = '%s'""" % (item_modele)
	return cond

def get_item_manufacturer(item_manufacturer):
	cond = """ and i.manufacturer = '%s'""" % (item_manufacturer)
	return cond
def get_item_version(vehicule_version):
	generation = vehicule_version[:-2]
	modele =generation[:-2]
	marque = modele[:-2]
	cond = """ and (i.name in (select parent from `tabVersion vehicule item` where version_vehicule = '{}')  or i.name in (select parent from `tabGeneration vehicule item` where generation_vehicule = '{}') or i.name in (select parent from `tabModele vehicule item` where modele_vehicule = '{}') or i.name in (select parent from `tabMarque vehicule item` where marque_vehicule = '{}') )""".format(vehicule_version,generation,modele,marque)
	return cond

def get_item_generation(vehicule_generation):
	modele =vehicule_generation[:-2]
	marque = modele[:-2]
	cond = """ and (i.name in (select parent from `tabVersion vehicule item` where nom_generation = '{}') or i.name in (select parent from `tabGeneration vehicule item` where generation_vehicule = '{}') or i.name in (select parent from `tabModele vehicule item` where modele_vehicule = '{}') or i.name in (select parent from `tabMarque vehicule item` where marque_vehicule= '{}') )""".format(vehicule_generation,vehicule_generation,modele,marque)
	return cond

def get_vehicule_modele(vehicule_modele):
	marque = vehicule_modele[:-2]
	cond = """ and (i.name in (select parent from `tabVersion vehicule item` where nom_modele = '{}') or i.name in (select parent from `tabGeneration vehicule item` where modele_vehicule = '{}') or i.name in (select parent from `tabModele vehicule item` where modele_vehicule = '{}') or i.name in (select parent from `tabMarque vehicule item` where marque_vehicule= '{}') )""".format(vehicule_modele,vehicule_modele,vehicule_modele,marque)
	return cond

def get_item_marque(vehicule_marque):
	cond = """ and (i.name in (select parent from `tabVersion vehicule item` where nom_marque = '{}') or i.name in (select parent from `tabModele vehicule item` where marque_vehicule = '{}') or i.name in (select parent from `tabGeneration vehicule item` where code_marque = '{}') or i.name in (select parent from `tabMarque vehicule item` where marque_vehicule = '{}') )""".format(vehicule_marque,vehicule_marque,vehicule_marque,vehicule_marque)
	return cond
	
	
def get_item_group_condition(pos_profile):
	cond = "and 1=1"
	item_groups = get_item_groups(pos_profile)
	if item_groups:
		cond = "and i.item_group in (%s)"%(', '.join(['%s']*len(item_groups)))

	return cond % tuple(item_groups)

def item_group_query(doctype, txt, searchfield, start, page_len, filters):
	item_groups = []
	cond = "1=1"
	pos_profile= filters.get('pos_profile')

	if pos_profile:
		item_groups = get_item_groups(pos_profile)

		if item_groups:
			cond = "name in (%s)"%(', '.join(['%s']*len(item_groups)))
			cond = cond % tuple(item_groups)

	return frappe.db.sql(""" select distinct name from `tabItem Group`
			where {condition} and (name like %(txt)s) limit {start}, {page_len}"""
		.format(condition = cond, start=start, page_len= page_len),
			{'txt': '%%%s%%' % txt})
