# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, throw
from frappe.utils import cint
from frappe.model.document import Document
import frappe.defaults
from frappe.utils import cint, flt
import json

class PriceList(Document):
	def validate(self):
		if not cint(self.buying) and not cint(self.selling):
			throw(_("Price List must be applicable for Buying or Selling"))

	def on_update(self):
		self.set_default_if_missing()
		self.update_item_price()

	def set_default_if_missing(self):
		if cint(self.selling):
			if not frappe.db.get_value("Selling Settings", None, "selling_price_list"):
				frappe.set_value("Selling Settings", "Selling Settings", "selling_price_list", self.name)

		elif cint(self.buying):
			if not frappe.db.get_value("Buying Settings", None, "buying_price_list"):
				frappe.set_value("Buying Settings", "Buying Settings", "buying_price_list", self.name)

	def update_item_price(self):
		frappe.db.sql("""update `tabItem Price` set currency=%s,
			buying=%s, selling=%s, modified=NOW() where price_list=%s""",
			(self.currency, cint(self.buying), cint(self.selling), self.name))

	def on_trash(self):
		def _update_default_price_list(module):
			b = frappe.get_doc(module + " Settings")
			price_list_fieldname = module.lower() + "_price_list"

			if self.name == b.get(price_list_fieldname):
				b.set(price_list_fieldname, None)
				b.flags.ignore_permissions = True
				b.save()

		for module in ["Selling", "Buying"]:
			_update_default_price_list(module)

@frappe.whitelist()
def switch_etat(item_code,etat):
	if item_code:
		if not etat or etat == "Approuve":
			frappe.db.set_value("Item", item_code, "prix_traite", "En cours")
			frappe.db.set_value("Item", item_code, "price_not_ready", 1)
			return "En cours"
		else:
			frappe.db.set_value("Item", item_code, "prix_traite", "Approuve")
			frappe.db.set_value("Item", item_code, "price_not_ready", 0)
			return "Approuve"

@frappe.whitelist()
def update_price(item_code,price_list,_price,qts,valuation):
	if item_code and price_list and _price:
		_price = flt(_price)
		if valuation:
			valuation = flt(valuation)
		if not qts:
			qts = 0
		else:
			qts = flt(qts)
		price = frappe.get_all("Item Price",fields=["name"],filters={"min_qty":qts,"item_code":item_code,"price_list":price_list})
		if price:
			if (not _price or _price == '0' or _price == 0 ) and price[0].name:
				frappe.delete_doc("Item Price", price[0].name)
				return "effacer - done -"
			else:
				price = frappe.get_doc("Item Price",price[0].name)
				price.price_list_rate = _price
				price.min_qty = qts
				price.save()
				if _price and valuation:
					
					ben = _price - valuation
					perv = round((ben / _price) * 100)
					perd = round((ben / valuation) * 100)
					return "modifie - done - \n\n\n COUTS: %s DA \n PRIX :  %s DA \n Benifice : %s DA \n Benifice nette: %s %%  \n Taux Benifice: %s %%" % (valuation or 'NA',_price,ben,perd,perv)
				else:
					return "modifie - done"
		elif _price:
			so = frappe.new_doc("Item Price")
			so.item_code = item_code
			so.price_list = price_list
			so.price_list_rate = _price
			so.min_qty = qts
			so.save()
			return "ajoute - done -"

		
	return "not done"

@frappe.whitelist()
def switch_etat_bulk(items):
	t = 0
	if isinstance(items, basestring):
		items = json.loads(items)
	if items:
		for item in items:
			frappe.db.set_value("Item", item, "prix_traite", "En cours")
			t += 1
	return "Termine pour %d" %  t
