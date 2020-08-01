# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ConversionArticles(Document):
	pass

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
	if refs2 and stock and ads:
		refs = refs2
		ads = ads.splitlines()
		clean = refs.splitlines()
		if clean:
			for idx,c in enumerate(clean):
				addr= ads[idx]
				if addr and c:
					mr = frappe.new_doc("Adresse Magasin")
					mr.update({
						"parent": c,
						"warehouse": stock,
						"adresse": addr
					})
					mr.insert()
				
