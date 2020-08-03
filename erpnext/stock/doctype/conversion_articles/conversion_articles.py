# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ConversionArticles(Document):
	save_items(self):
		if self.articles:
			for item in self.articles:
				if item and item.ref and item.adr and item.publique and item.gros:
					c = item.ref.replace(" ","").replace("-","").replace("_","").replace("/","").replace(".","")
					code = frappe.db.get_value('Item', {"clean_manufacturer_part_number": c}, ['item_code'])
					article = frappe.get_doc("Item",code)
					if article:
						# adresse magasin
						if not article.table_adresse_magasin or (item.adr not in {a.adresse for a in article.table_adresse_magasin}):
							row = article.append('table_adresse_magasin',{})
							row.warehouse = self.stock
							row.adresse = item.adr
						# prix
						if item.publique:
							price = frappe.get_all("Item Price",fields=["name"],filters={"min_qty":0,"item_code":article.item_code,"price_list":"PRIX PUBLIQUE"})
							if price:
								price = frappe.get_doc("Item Price",price[0].name)
								price.price_list_rate = item.publique
								price.min_qty = 0
								price.save()
							else:
								so = frappe.new_doc("Item Price")
								so.item_code = article.item_code
								so.price_list = "PRIX PUBLIQUE"
								so.price_list_rate = item.publique
								so.save()
						if item.gros:
							price = frappe.get_all("Item Price",fields=["name"],filters={"min_qty":0,"item_code":article.item_code,"price_list":"PRIX EN GROS"})
							if price:
								price = frappe.get_doc("Item Price",price[0].name)
								price.price_list_rate = item.gros
								price.min_qty = 0
								price.save()
							else:
								so = frappe.new_doc("Item Price")
								so.item_code = article.item_code
								so.price_list = "PRIX EN GROS"
								so.price_list_rate = item.gros
								so.save()
						article.save()
		frappe.msgprint("Done")
		

@frappe.whitelist()
def get_converstion(refs):
	result = ""
	if refs:
		clean = refs.splitlines()		
		if clean:
			for c in clean:
				if c:
					c = c.replace(" ","").replace("-","").replace("_","").replace("/","").replace(".","")
					code = frappe.db.get_value('Item', {"clean_manufacturer_part_number": c}, ['item_code'])
					result += "%s\n" % (code or '')
				else:
					
					result += "\n"
	return result

@frappe.whitelist()
def set_address(refs2,stock,ads):
	i = 0
	if refs2 and stock and ads:
		refs = refs2
		ads = ads.splitlines()
		clean = refs.splitlines()
		if clean:
			for idx,c in enumerate(clean):
				addr= ads[idx]
				if addr and c:
					other_comp = frappe.get_doc("Item",c)
					row = other_comp.append('table_adresse_magasin',{})
					row.warehouse = stock
					row.adresse = addr
					other_comp.save()
					i = i +1
	return "Done %d" % i
