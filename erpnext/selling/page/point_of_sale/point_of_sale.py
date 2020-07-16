# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, json
from frappe.utils.nestedset import get_root_of
from frappe.utils import cint
from erpnext.accounts.doctype.pos_profile.pos_profile import get_item_groups
from erpnext.stock.get_item_details import get_price_list_rate_for
from frappe.utils.pdf import get_pdf
import pdfkit
import os

from six import string_types


@frappe.whitelist()
def get_price_info(customer,price_list,transaction_date,qty,item_code,uom):
	args = {
		"price_list":price_list,
		"customer":customer,
		"qty":qty,
		"uom" : uom,
		"transaction_date":transaction_date
	}
	return get_price_list_rate_for(args,item_code)
	
	
@frappe.whitelist()
def open_item_info(item_code):
	if item_code:
		item = frappe.client.get("Item",item_code)
		image = ''
		fabricant_logo = ''
		if item.fabricant_logo:
			fabricant_logo ='<img src="'+item.fabricant_logo+'">'
		if item.image:
			image ='<img src="'+item.image+'">'
		_modal =""" 
						<button type="button" data-item-code="{item_code}" class="btn btn-primary btn-sm btn-versions-list" > 
							<span class="hidden-xs">Vehicules Supportees</span>
						</button>
						<button  class="btn btn-default btn-sm  btn-info-price" data-item-code="{item_code}"  style="margin-right: 5px;">Afficher les prix</button>
						<button  class="btn btn-default btn-sm  btn-open" data-item-code="{item_code}"  style="margin-right: 5px;">Editer Article</button>
<br>
						<table class="table table-bordered table-condensed">
							<tr><td>{item_name}</td><td>
									 {image} 
								</td></tr>
							<tr> 
								<td>
									<label>{item_code}</label>
								</td>
								<td>
									<label>{manufacturer_part_no}</label>
								</td>
							</tr> 
						</table>

						<table class="table table-bordered table-condensed">
							<tr> 
								<td>
									<label>OEM</label>
								</td>
								<td>
									{oem_text}
								</td>
								<td></td>
							</tr>
							<tr> 
								<td>
									<label>Fabricant</label>
								</td>
								<td>
									{manufacturer}
								</td>
								<td>
									{fabricant_logo}
								</td>
							</tr>
							<tr> 
								<td>
									<label>Critere</label>
								</td>
								<td>
									{critere_text}
								</td>
								<td>

								</td>
							</tr>
						</table>

						<hr>	
						<label>Complementent </label>
						<div>{articles_text}</div>
						<hr>	
						<label>Composants </label>
						<div>{composant_text}</div>
						<hr>""".format(item_name=item.item_name,image=image,item_code=item_code,manufacturer_part_no=item.manufacturer_part_no
							    ,oem_text=item.oem_text,manufacturer=item.manufacturer,fabricant_logo=fabricant_logo,critere_text=item.critere_text,articles_text=item.articles_text,composant_text=item.composant_text)
		d = frappe.msgprint(_modal)
		return d
		
			


@frappe.whitelist()
def get_item_prices(item_code,selling=1):
	res = {}
	item = frappe.client.get("Item",item_code)
	res.update({'item':item})
	text = ''
	prices = frappe.db.get_all("Item Price",filters={"item_code":item_code,"selling":selling},fields=["currency","name","price_list_rate","min_qty","price_list"])
	if prices:
		for p in prices:
			text += "<li>%s +%s      <strong>%s</strong> %s </li>" % ((p.price_list or '').ljust(25,str("-")),(str(p.min_qty) or '').ljust(20,str(" ")),(str(p.price_list_rate) or '').ljust(10,str(" ")),p.currency)
	res.update({'price':text})
	return res

@frappe.whitelist()
def get_item_info(item_code,price_list):
	res = {}
	item = frappe.client.get("Item",item_code)
	res.update({'item':item})
	text = ''
	prices = frappe.db.get_all("Item Price",filters={"item_code":item_code,"selling":1,"price_list":price_list},fields=["currency","name","price_list_rate","min_qty","price_list"])
	if prices:
		for p in prices:
			text += "<li>%s +%s      <strong>%s</strong> %s </li>" % ((p.price_list or '').ljust(25,str("-")),(str(p.min_qty) or '').ljust(20,str(" ")),(str(p.price_list_rate) or '').ljust(10,str(" ")),p.currency)
	res.update({'price':text})
	return res
	
@frappe.whitelist()
def print_address_magasin(items,qts,pos_profile,customer):
	items = items.split(",")
	qts = qts.split(",")
	warehouse = frappe.get_value("POS Profile",pos_profile,"warehouse")
	result = {}
	failed = ""
	if items:
		for idx, item in enumerate(items):
			q = qts[idx]
			adr = frappe.db.get_value("Adresse Magasin", {"parent": item,"warehouse":warehouse}, 'adresse')
			fabricant = frappe.db.get_value("Item", {"item_code": item}, 'manufacturer')
			ref = frappe.db.get_value("Item", {"item_code": item}, 'manufacturer_part_no')
			if adr:
				result.update({
						item:{
					       		"qts":q,
					       		"adr":adr,
							"fabricant": fabricant,
							"ref":ref
						}
					      })
	else:
		failed = "no items %s %s %s" % (result,items,warehouse)
		
	if result:
		final_html = prepare_bulk_print_html(result,customer,warehouse)
		pdf_options = { 
						"page-height" : "15.0cm",
						"page-width" : "8.0cm",
						"margin-top": "10mm",
						"margin-bottom": "10mm",
						"margin-left": "5mm",
						"margin-right": "5mm",
						"no-outline": None,
						"encoding": "UTF-8",
						"title": "ADRESSE",
					}

		frappe.local.response.filename = "{filename}.pdf".format(filename="catalogue_address")
		frappe.local.response.filecontent = dignity_get_pdf(final_html, options=pdf_options) #get_pdf(final_html, pdf_options)
		frappe.local.response.type = "download"
	else:
		failed = "no result %s %s %s" % (result,items,warehouse)
		
	if failed:
		return failed
		
def prepare_bulk_print_html(names,customer,warehouse):
	final_html = frappe.render_template("""
	<div style="font-size:10px">
	<p style="text-align:center;font-weight:bold">MON VEHICULE</p>
	<p style="text-align:center">{{warehouse}}</p>
	<p style="text-align:center">Client : {{customer}}</p>
	
	{% for sc in names %}<small>{{sc}} : <span style="font-weight:bold"">{{names[sc].qts}} <span> ************************ <span>{{names[sc].adr}}<span>
	</small><br>{{names[sc].fabricant}} / {{names[sc].ref}}<br>----------------------------------------------------------<br>{% endfor %}
	</div>
	""", {"names":names,"warehouse":warehouse,"customer":customer})
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

@frappe.whitelist()
def vente_perdue(cause,article,profile):
	vp = frappe.new_doc("Vente Perdue")
	vp.cause = cause
	vp.article = article
	vp.declarer_par = profile
	vp.save()
	return
	
	
@frappe.whitelist()
def get_complements(item_code):
	if not item_code:
		return []
	versions = frappe.get_all("Composant",filters={"parent":item_code,"parentfield":"articles"},fields=["item","parent"])
	manufacturer = frappe.db.get_value('Item', item_code, "manufacturer")
	items = []
	for version in versions:
		_size = len(version.item)
		if _size == 11:
			item = frappe.get_all("Item",filters={"manufacturer":manufacturer,"variant_of":version.item},fields=["*"])
			items.extend(item)
		else:
			item = frappe.get_all("Item",filters={"manufacturer":manufacturer,"item_code":version.item},fields=["*"])
			items.extend(item)
	return items


@frappe.whitelist()
def get_composants(item_code):
	if not item_code:
		return []
	versions = frappe.get_all("Composant",filters={"parent":item_code,"parentfield":"composant"},fields=["item","parent"])
	manufacturer = frappe.db.get_value('Item', item_code, "manufacturer")
	items = []
	for version in versions:
		_size = len(version.item)
		if _size == 11:
			item = frappe.get_all("Item",filters={"manufacturer":manufacturer,"variant_of":version.item},fields=["*"])
			items.extend(item)
		else:
			item = frappe.get_all("Item",filters={"manufacturer":manufacturer,"item_code":version.item},fields=["*"])
			items.extend(item)
	return items

@frappe.whitelist()
def get_vehicule_details(item_code):
	versions = frappe.get_all("Version vehicule item",filters={"parent":item_code},fields=["*"])
	generations = frappe.get_all("Generation vehicule item",filters={"parent":item_code},fields=["*"])
	modeles = frappe.get_all("Modele vehicule item",filters={"parent":item_code},fields=["*"])
	marques = frappe.get_all("Marque vehicule item",filters={"parent":item_code},fields=["*"])
	
	return versions,generations,modeles,marques

@frappe.whitelist()
def get_stock_details(item_code,pos_profile):
	
	my_warehouses = frappe.get_all("Entrepot Pofile PDV",fields=['*'],filters={"parent":pos_profile})
	pwh = frappe.get_value("POS Profile",pos_profile,"warehouse")
	aw = []
	if pwh:
		aw.append(pwh)
	
	if my_warehouses:
		aw.extend([x.warehouse for x in my_warehouses if x.warehouse not in aw])
	#aw = set(aw)
	#magasin = frappe.db.get_single_value("Stock Settings", "entrepot_magasin")
	#if magasin:
	#	allmagasin = frappe.get_all("Warehouse",fields=['name'],filters={"parent_warehouse":magasin})
	#	if allmagasin:
	#		aw.extend([x.name for x in allmagasin])
	#depot = frappe.db.get_single_value("Stock Settings", "entrepot_depot")
	#if depot:
	#	alldepot = frappe.get_all("Warehouse",fields=['name'],filters={"parent_warehouse":depot})
	#	if alldepot:
	#		aw.extend([x.name for x in alldepot])
	rest = frappe.db.sql(''' select warehouse, actual_qty from `tabBin` where item_code='{item_code}' and warehouse in ({wr})'''.format(item_code=item_code,   wr=", ".join(['%s']*len(aw))), tuple(aw), as_dict=1 )
	#res_depots = frappe.db.sql(""" select warehouse, actual_qty from `tabBin` where item_code=%s  and warehouse in (%s)   """,(item_code, ', '.join(['"%s"' % d for d in aw])) , as_dict=1)
	for r in rest:
		_item = next(w for w in my_warehouses if w.warehouse==r.warehouse)
		if _item and not _item.voir_qts:
			r.actual_qty = "Disponible" if r.actual_qty > 0 else "Non Disponible"
	return rest,aw

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
def make_sales_order(customer,items,pos_profile):
	#frappe.msgprint(items)
	items = json.loads(items)
	
	so = frappe.new_doc("Sales Order")
	so.customer = customer
	if pos_profile:
		warehouse = frappe.get_value("POS Profile",pos_profile,"warehouse")
		so.set_warehouse = warehouse
	
	for item in items:
		item = frappe._dict(item)
		item.doctype="Sales Order Item"
		item.parent=so.name
		item.parenttype = "Sales Order"
		
		so.append('items', item)
	
	so.save()
	return so

@frappe.whitelist()
def get_items(start, page_length, price_list, item_group, search_value="", pos_profile=None,item_manufacturer=None,item_modele=None, vehicule_marque=None, vehicule_modele=None, vehicule_generation=None, vehicule_version=None,item_oem=None,parent_item_group=None):
	data = dict()
	warehouse = ""
	display_items_in_stock = 0
	lft = ''
	rgt = ''
	# modification temporaire a modifier
	#if search_value:
	#	search_value = search_value.replace(" ","").replace("-","")
	
	if item_oem or search_value or item_modele:
		vehicule_version = None
		vehicule_generation = None
		vehicule_marque = None
		vehicule_modele=None
		item_group = None
		item_manufacturer = None

	if pos_profile:
		warehouse, display_items_in_stock = frappe.db.get_value('POS Profile', pos_profile, ['warehouse', 'display_items_in_stock'])

	if parent_item_group:
		lft, rgt = frappe.db.get_value('Item Group', parent_item_group, ['lft', 'rgt'])
	
	if item_group and not frappe.db.exists('Item Group', item_group):
		item_group = get_root_of('Item Group')
	elif item_group:
		lft, rgt = frappe.db.get_value('Item Group', item_group, ['lft', 'rgt'])

	if search_value:
		data = search_serial_or_batch_or_barcode_number(search_value)

	item_code = data.get("item_code") if data.get("item_code") else (search_value or '').strip()
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
	if item_oem:
		condition += get_item_oem(item_oem)

	if vehicule_version:
		condition += get_item_version(vehicule_version)
	elif vehicule_generation:
		condition += get_item_generation(vehicule_generation)
	elif vehicule_modele:
		condition += get_vehicule_modele(vehicule_modele)
	elif vehicule_marque:
		condition += get_item_marque(vehicule_marque)
	

	group_filter = ""
	if item_group:
		group_filter =""" and i.item_group in (select name from `tabItem Group` where lft >= {lft} and rgt <= {rgt}) """.format(lft=lft, rgt=rgt)
	# locate function is used to sort by closest match from the beginning of the value


	if display_items_in_stock == 0:
		res = frappe.db.sql("""select i.name as item_code,item_adr.adresse,item_adr.warehouse,i.nbr_variante ,i.qts_total,i.designation_commerciale,i.variant_of,i.has_variants, i.item_name, i.image , i.idx as idx,i.clean_manufacturer_part_number, i.composant_text,i.articles_text,
			i.is_stock_item, item_det.price_list_rate, item_det.currency, i.oem_text,i.titre_article,i.manufacturer,i.manufacturer_part_no,i.fabricant_logo,i.critere_text ,item_bin.actual_qty
			from `tabItem` i LEFT JOIN (select item_code, price_list_rate,min_qty, currency from
					`tabItem Price`	where min_qty=0 and price_list=%(price_list)s  ) item_det
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
				{group_filter}
		        	and {condition}  limit {start}, {page_length}""".format(start=start,page_length=page_length,lft=lft, rgt=rgt,condition=condition,group_filter=group_filter),
			{
				'item_code': item_code,
				'price_list': price_list,
				'warehouse':warehouse
			} , as_dict=1)

		res = {
		'items': res
		}

	elif display_items_in_stock == 1:
		query = """select i.name as item_code,i.variant_of,item_adr.adresse,item_adr.warehouse,i.qts_total,i.designation_commerciale,i.nbr_variante ,i.has_variants, i.item_name, i.image , i.idx as idx,i.clean_manufacturer_part_number,i.composant_text,i.articles_text,
				i.is_stock_item, item_det.price_list_rate, item_det.currency, i.oem_text,i.titre_article,i.manufacturer,i.manufacturer_part_no,i.fabricant_logo , i.critere_text  
				from `tabItem` i LEFT JOIN
					(select item_code, price_list_rate,min_qty, currency from
						`tabItem Price`	where  min_qty=0 and price_list=%(price_list)s  ) item_det
				ON
					(item_det.item_code=i.name or item_det.item_code=i.variant_of)  INNER JOIN
				
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
				{group_filter}				
				and {condition}  limit {start}, {page_length}""".format(start=start,page_length=page_length,lft=lft, 	rgt=rgt, condition=condition,group_filter=group_filter),
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
	if not search_value and (item_manufacturer or item_modele or vehicule_version or vehicule_generation or vehicule_modele or vehicule_marque):
		_items = res['items']
		_items.sort(key=lambda x: x.actual_qty, reverse=True)
		res.update({
			'items':_items
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
	
	item_code = item_code.replace("(","").replace(")","")
	words = item_code.split("  ")
	clean = item_code.replace(" ","")
	
	keyword = '* *'.join(w.rstrip('-()#. ').lstrip('-()#. ') for w in words)
	keyword = "*%s*" % keyword
	if len(words) > 1:
		condition = """ (  i.item_code = '{}' or i.item_code LIKE '%%{}%%' or i.clean_manufacturer_part_number = '{}' or i.clean_manufacturer_part_number LIKE '%%{}%%' or  i.manufacturer_part_no = '{}' or  i.manufacturer_part_no LIKE '%%{}%%' or i.oem_text = '{}'  or i.oem_text LIKE '%%{}%%' or MATCH(i.nom_generique_long) AGAINST('{}' IN BOOLEAN MODE)  )""".format(item_code,item_code,clean,item_code,item_code,item_code,item_code,item_code,keyword)
	else:
		condition = """ (  i.item_code = '{}' or i.item_code LIKE '%%{}%%' or i.clean_manufacturer_part_number = '{}' or i.clean_manufacturer_part_number LIKE '%%{}%%' or  i.manufacturer_part_no = '{}' or  i.manufacturer_part_no LIKE '%%{}%%' or i.oem_text = '{}'  or i.oem_text LIKE '%%{}%%'   )""".format(clean,clean,clean,clean,clean,clean,clean,clean)
		
	#condition = """ ( i.clean_manufacturer_part_number LIKE '%%{}%%' or i.oem_text LIKE '%%{}%%' or  MATCH(i.name,i.item_name,i.nom_generique_long,i.manufacturer_part_no,i.clean_manufacturer_part_number,i.oem_text) AGAINST('({})' IN NATURAL LANGUAGE MODE)  )""".format(item_code,item_code,item_code)

	return '%%%s%%'%(frappe.db.escape(item_code)), condition

def get_item_modele(item_modele):
	cond = """ and i.variant_of = '%s'""" % (item_modele)
	return cond

def get_item_manufacturer(item_manufacturer):
	cond = """ and i.manufacturer = '%s'""" % (item_manufacturer)
	return cond

def get_item_oem(item_oem):
	#frappe.msgprint(item_oem)
	cond = """ and i.oem_text LIKE '%%{}%%' """.format(item_oem)
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
	pcond = "1=1"
	pos_profile= filters.get('pos_profile')
	

	if pos_profile:
		item_groups = get_item_groups(pos_profile)

		if item_groups:
			cond = "name in (%s)"%(', '.join(['%s']*len(item_groups)))
			cond = cond % tuple(item_groups)
		if filters.get('parent'):
			pcond = """ parent_item_group LIKE '%%{}%%' """.format(filters.get('parent'))

	return frappe.db.sql(""" select distinct name from `tabItem Group`
			where {condition} and {pcond} and is_group=0 and (name like %(txt)s) limit {start}, {page_len}"""
		.format(condition = cond,pcond=pcond, start=start, page_len= page_len),
			{'txt': '%%%s%%' % txt})
