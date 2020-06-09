# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from frappe.utils import flt, nowdate, add_days
from frappe.model.mapper import get_mapped_doc
from erpnext.stock.stock_balance import update_bin_qty, get_indented_qty
from erpnext.controllers.buying_controller import BuyingController
from erpnext.buying.utils import validate_for_items

form_grid_templates = {
	"items": "templates/form_grid/item_grid.html"
}

class SupplierQuotation(BuyingController):
	def validate(self):
		super(SupplierQuotation, self).validate()

		if not self.status:
			self.status = "Draft"

		from erpnext.controllers.status_updater import validate_status
		validate_status(self.status, ["Draft", "Submitted", "Stopped",
			"Cancelled"])

		validate_for_items(self)
		self.validate_with_previous_doc()
		self.validate_uom_is_integer("uom", "qty")
		_items = []
		for item in self.items:
			if not item.oem:
				oem = frappe.db.get_value('OEM',{'parent': item.item_code, 'important':1},'oem')
				item.oem = oem
			if not item.qts_original or item.qts_original == 0:
				item.qts_original = int(item.qty * 0.25)
				if item.qts_original <= 0:
					item.qts_original = 2
			if item.prix_fournisseur and not item.offre_fournisseur_initial:
				item.offre_fournisseur_initial = item.prix_fournisseur
			if item.prix_fournisseur and item.prix_fournisseur != item.rate:
				item.rate = item.prix_fournisseur
			if not item.confirmation:
				item.confirmation = "En cours"
			if item.confirmation == "Annule":
				item.qty = 0
			if item.qty == 0 and item.confirmation == "Approuve":
				throw("Attention, il existe l'article %s avec qts %d et confirmation %s" % (item.item_code,item.qty,item.confirmation))
			if self.manufacturer:
				if item.fabricant == self.manufacturer:
					if not any(x.name == item.name for x in _items):
						_items.append(item)
		
		if self.manufacturer:
			self.items = _items
			
	def set_resultat(self):
		resultat = 'NA'
		if self.docstatus == 1:
			resultat = "Termine P3"
		else:
			encours = sum(1 for item in self.items if item.confirmation == "En cours" or not item.confirmation or item.confirmation=='') or 0
			offre = sum(1 for item in self.items if item.prix_fournisseur > 0) or 0
			change =  sum(1 for item in self.items if item.prix_fournisseur != item.offre_fournisseur_initial and item.offre_fournisseur_initial > 0) or 0
			total = len(self.items) or 0
			en_negociation = sum(1 for item in self.items if item.confirmation == "En negociation") or 0
			approuve = sum(1 for item in self.items if item.confirmation == "Approuve") or 0
			annule = sum(1 for item in self.items if item.confirmation == "Annule") or 0
			#((@en_cours = @total) and (@offre=0) and (mr.etat_mail !='Email Envoye')) THEN 'A Envoyer P1'
			if encours == total and offre == 0 and self.etat_mail !='Email Envoye':
				resultat = 'A Envoyer P1'
			#WHEN ((@en_cours = @total) and (@offre=0) and (mr.etat_mail ='Email Envoye')) THEN 'En attente de repense P1'
			elif encours == total and offre==0 and self.etat_mail =='Email Envoye':
				resultat = 'En attente de repense P1'
			#WHEN (@en_cours > 0 and @en_cours < @total and @offre>0 and (mr.etat_mail !='Email Envoye')) THEN 'A Traite P1'
			elif encours >0 and change==0 and  offre>0 and self.etat_mail !='Email Envoye':
				resultat = 'A Traite P1'
			#WHEN ((@en_cours = 0) and @change=0 and (@offre>0) and (mr.etat_mail !='Email Envoye')) THEN 'A Envoyer P2'
			elif encours==0 and change==0 and offre>0 and self.etat_mail !='Email Envoye':
				resultat = 'A Envoyer P2'
			#WHEN ((@en_cours = 0) and (@offre>0) and (mr.etat_mail ='Email Envoye')) THEN 'En attente de repense P2'
			elif encours==0 and offre>0 and self.etat_mail =='Email Envoye':
				resultat = 'En attente de repense P2'
			#WHEN ((@en_cours = 0) and (@offre>0) and @change >0 and (@annule + @approuve < @total) and (mr.etat_mail !='Email Envoye')) THEN 'A Traite P2'
			elif offre>0 and change>0 and (approuve+annule) < total and self.etat_mail !='Email Envoye':
				resultat = 'A Traite P2'
			#WHEN ((@en_cours = 0) and (@offre>0) and (@annule + @approuve = @total) and (mr.etat_mail !='Email Envoye')) THEN 'Envoyer la confirmation'
			elif encours==0 and offre>0 and  (approuve+annule) == total and self.etat_mail !='Email Envoye':
				resultat = 'Envoyer la confirmation'
			#WHEN ((@en_cours = 0) and (@offre>0) and (@annule + @approuve = @total) and (mr.etat_mail ='Email Envoye')) THEN 'Termine P3'
			elif encours==0 and offre>0 and  (approuve+annule) == total and self.etat_mail =='Email Envoye':
				resultat = 'Termine P3'
			else:
				resultat = 'NA'
		frappe.db.set_value("Supplier Quotation",self.name,"resultat",resultat)

        def on_update(self):
		#if self.etat_mail == "Email Envoye":
		#	throw("Impossible de modifier la consultation si l'email est envoye ! Veuillez marquer comme non envoye.")
		frappe.enqueue("erpnext.buying.doctype.supplier_quotation.supplier_quotation.on_update_consultation",items=self.items,pname=self.name,timeout=10000)
		frappe.enqueue("erpnext.buying.doctype.supplier_quotation.supplier_quotation.on_update_dv",items=self.items,timeout=10000)
		self.set_resultat()


	def on_submit(self):
		self.validate_approuve()
		frappe.db.set(self, "status", "Submitted")
		self.update_rfq_supplier_status(1)
		self.update_requested_qty()
		frappe.enqueue("erpnext.buying.doctype.supplier_quotation.supplier_quotation.update_mr",doc=self,timeout=10000)
                #self.update_mr()
	
	def update_requested_qty(self, mr_item_rows=None):
		"""update requested qty (before ordered_qty is updated)"""
		item_wh_list = []
		for d in self.get("items"):
			if (not mr_item_rows or d.name in mr_item_rows) and [d.item_code, d.warehouse] not in item_wh_list \
					and frappe.db.get_value("Item", d.item_code, "is_stock_item") == 1 and d.warehouse:
				item_wh_list.append([d.item_code, d.warehouse])

		for item_code, warehouse in item_wh_list:
			update_bin_qty(item_code, warehouse, {
				"indented_qty": get_indented_qty(item_code, warehouse)
			})
	def validate_approuve(self):
		encours = sum(1 for i in self.items if (i.confirmation =="En cours" or i.confirmation =="En negociation"))
		if encours > 0:
			throw("Il existe des articles avec confirmation 'En cours/En negociation', Veuillez modifier la valeur")
	def on_trash(self):
		dms = []
                for item in self.items:
		    if item.material_request:
			dms.append(item.material_request)
                    if item.material_request_item:
                        mr = frappe.get_doc("Material Request Item",item.material_request_item)
                        if mr and mr.docstatus != 2:
                            mr.consulted = 0
                            mr.flags.ignore_mandatory = 1
                            mr.flags.ignore_validate = 1
                            mr.flags.ignore_links = 1
                            mr.save()
		if dms:
			setdms = set(dms)
			dms = list(setdms)
			for d in dms:
				if d:
					demande = frappe.get_doc("Material Request",d)
					demande.handle_per_consulted()

	def on_cancel(self):
		frappe.db.set(self, "status", "Cancelled")
		self.update_requested_qty()
		dms = []
                for item in self.items:
		    if item.material_request:
			dms.append(item.material_request)
                    if item.material_request_item:
                        mr = frappe.get_doc("Material Request Item",item.material_request_item)
                        if mr and mr.docstatus != 2:
				try:
					mr.consulted = 0
					mr.flags.ignore_mandatory = 1
					mr.flags.ignore_validate = 1
					mr.flags.ignore_links = 1
					mr.save()
				except:
					print("An exception occurred")

		self.update_rfq_supplier_status(0)
		if dms:
			setdms = set(dms)
			dms = list(setdms)
			for d in dms:
				if d:
					demande = frappe.get_doc("Material Request",d)
					try:
						demande.handle_per_consulted()
					except:
						print("An exception occurred")


	def validate_with_previous_doc(self):
		super(SupplierQuotation, self).validate_with_previous_doc({
			"Material Request": {
				"ref_dn_field": "prevdoc_docname",
				"compare_fields": [["company", "="]],
			},
			"Material Request Item": {
				"ref_dn_field": "prevdoc_detail_docname",
				"compare_fields": [["item_code", "="], ["uom", "="]],
				"is_child_table": True
			}
		})
	def update_rfq_supplier_status(self, include_me):
		rfq_list = set([])
		for item in self.items:
			if item.request_for_quotation:
				rfq_list.add(item.request_for_quotation)
		for rfq in rfq_list:
			doc = frappe.get_doc('Request for Quotation', rfq)
			doc_sup = frappe.get_all('Request for Quotation Supplier', filters=
				{'parent': doc.name, 'supplier': self.supplier}, fields=['name', 'quote_status'])

			doc_sup = doc_sup[0] if doc_sup else None
			if not doc_sup:
				frappe.throw(_("Supplier {0} not found in {1}").format(self.supplier,
					"<a href='desk#Form/Request for Quotation/{0}'> Request for Quotation {0} </a>".format(doc.name)))

			quote_status = _('Received')
			for item in doc.items:
				sqi_count = frappe.db.sql("""
					SELECT
						COUNT(sqi.name) as count
					FROM
						`tabSupplier Quotation Item` as sqi,
						`tabSupplier Quotation` as sq
					WHERE sq.supplier = %(supplier)s
						AND sqi.docstatus = 1
						AND sq.name != %(me)s
						AND sqi.request_for_quotation_item = %(rqi)s
						AND sqi.parent = sq.name""",
					{"supplier": self.supplier, "rqi": item.name, 'me': self.name}, as_dict=1)[0]
				self_count = sum(my_item.request_for_quotation_item == item.name
					for my_item in self.items) if include_me else 0
				if (sqi_count.count + self_count) == 0:
					quote_status = _('Pending')
			if quote_status == _('Received') and doc_sup.quote_status == _('No Quote'):
				frappe.msgprint(_("{0} indicates that {1} will not provide a quotation, but all items \
					have been quoted. Updating the RFQ quote status.").format(doc.name, self.supplier))
				frappe.db.set_value('Request for Quotation Supplier', doc_sup.name, 'quote_status', quote_status)
				frappe.db.set_value('Request for Quotation Supplier', doc_sup.name, 'no_quote', 0)
			elif doc_sup.quote_status != _('No Quote'):
				frappe.db.set_value('Request for Quotation Supplier', doc_sup.name, 'quote_status', quote_status)

def get_list_context(context=None):
	from erpnext.controllers.website_list_for_contact import get_list_context
	list_context = get_list_context(context)
	list_context.update({
		'show_sidebar': True,
		'show_search': True,
		'no_breadcrumbs': True,
		'title': _('Supplier Quotation'),
	})

	return list_context

@frappe.whitelist()
def update_mr(doc):
	man = doc.manufacturer
	mr = []
	allmr = []
	for item in doc.items:
	    if item.material_request_item:
		mr.append(item.material_request_item)
	    if item.material_request:
		allmr.append(item.material_request)

	if man:
		of_manu = frappe.get_all("Material Request Item",filters={"docstatus":("!=",2),"consulted":0,"creation":("<=",doc.creation),"fabricant":man},fields=["name","consultation"])
		for m in of_manu:
		    try:
			    #if m.name not in mr:
			    ori = frappe.get_doc("Material Request Item",m.name)
			    if m.name in mr:
				ori.consultation = doc.name
			    else:
				ori.consultation = ""
			    ori.consulted = 1
			    ori.flags.ignore_mandatory = True
			    ori.flags.ignore_validate = True
			    ori.flags.ignore_links = True
			    if ori.docstatus != 2:
				ori.save()
		    except:
			    print("An exception occurred")
		    #except:
			#ori.parent = ""
			#frappe.msgprint("Validation demande de materiel echoue !")
		#frappe.delete_doc("Material Request Item",m.name,force=1)
	    #else:
		#try:
	    #        ori.consultation = self.name
	    #        ori.consulted = 1
	    #        ori.save()
		#except:
		#    ori.consultation = self.name
	for mat in allmr:
	    material = frappe.get_doc("Material Request",mat)
	    if material:
		try:
		    material.handle_per_consulted()
		    #material.status = "Consultation"
		    material.save()
		except:
		    print("An exception occurred")
			
			
@frappe.whitelist()
def on_update_consultation(items,pname):
	#print("doing update xxx consultation")
	bc = []
	dms = []
	for item in items:
		try:
			if item.material_request:
				dms.append(item.material_request)
			if item.handled_cmd:
				bc.append(item.handled_cmd)
			wg = item.weight_per_unit
			if wg and wg > 0:
				frappe.db.sql(""" update `tabItem` set weight_per_unit = %s
			where item_code=%s""",(wg,item.item_code))
			wgi = item.weight_uom
			if wgi:
				frappe.db.sql(""" update `tabItem` set weight_uom = %s
			where item_code=%s""",(wgi,item.item_code))
			if item.material_request_item:
				print("item req : %s" % item.material_request_item)
				mr = frappe.get_doc("Material Request Item",item.material_request_item)
				if mr and mr.docstatus != 2:
					mr.consultation = pname
					mr.consulted = 1
					mr.flags.ignore_links = True
					mr.flags.ignore_mandatory = True
					mr.flags.ignore_validate = True
					mr.save()
		except:
			print("An exception occurred")
	if dms:
		setdms = set(dms)
		dms = list(setdms)
		for d in dms:
			if d:
				try:
					demande = frappe.get_doc("Material Request",d)
					demande.handle_per_consulted()
				except:
					print("An exception occurred")

@frappe.whitelist()
def on_update_dv(items):		
	for i in items:
		i.ref_devis = i.parent
		i.save()
			
@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.ignore_pricing_rule = 1
		items = []
		for i in target.items:
			if not i.handled and i.qty > 0 and i.confirmation == "Approuve":
				items.append(i)
		target.items = items
		target.run_method("set_missing_values")
		target.run_method("get_schedule_dates")
		target.run_method("calculate_taxes_and_totals")

	def update_item(obj, target, source_parent):
		target.stock_qty = flt(obj.qty) * flt(obj.conversion_factor)

	doclist = get_mapped_doc("Supplier Quotation", source_name,		{
		"Supplier Quotation": {
			"doctype": "Purchase Order",
			"validation": {
				"docstatus": ["=", 1],
			}
		},
		"Supplier Quotation Item": {
			"doctype": "Purchase Order Item",
			"field_map": [
				["name", "supplier_quotation_item"],
				["parent", "supplier_quotation"],
				["pays", "pays"],
				["material_request", "material_request"],
				["material_request_item", "material_request_item"],
				["sales_order", "sales_order"]
			],
			"postprocess": update_item
		},
		"Purchase Taxes and Charges": {
			"doctype": "Purchase Taxes and Charges",
		},
	}, target_doc, set_missing_values)

	return doclist

@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
	doclist = get_mapped_doc("Supplier Quotation", source_name, {
		"Supplier Quotation": {
			"doctype": "Quotation",
			"field_map": {
				"name": "supplier_quotation",
			}
		},
		"Supplier Quotation Item": {
			"doctype": "Quotation Item",
			"condition": lambda doc: frappe.db.get_value("Item", doc.item_code, "is_sales_item")==1,
			"add_if_empty": True
		}
	}, target_doc)

	return doclist

#delete from devis
@frappe.whitelist()
def set_item_achat(item_code):
	if item_code:
		frappe.delete_doc("Supplier Quotation Item", item_code)
		return "ARTICLE SUPPRIME : %s" % item_code
	
@frappe.whitelist()
def set_item_demande(item_code,qty):
	if item_code and qty:
		item = frappe.get_doc("Supplier Quotation Item",item_code)
		if item:
			item.qty = float(qty)
			if item.qty == 0:
				item.confirmation = "Annule"
			else:
				item.rate = item.prix_fournisseur
				item.confirmation = "Approuve"
			item.save()
			frappe.db.set_value("Supplier Quotation", item.parent, "etat_mail", "Email Non Envoye")
			sq = frappe.get_doc("Supplier Quotation",item.parent)
			if sq:
				sq.set_resultat()
			return "Nouvelle Qts enregistree"
			
@frappe.whitelist()
def approuver_item(item_code):
	if item_code:
		item = frappe.get_doc("Supplier Quotation Item",item_code)
		if item:
			if item.qty == 0:
				return "Attention impossible d'approuver avec la Qts egale 0"
			item.confirmation = "Approuve"
			item.rate = item.prix_fournisseur
			item.save()
			frappe.db.set_value("Supplier Quotation", item.parent, "etat_mail", "Email Non Envoye")
			sq = frappe.get_doc("Supplier Quotation",item.parent)
			if sq:
				sq.set_resultat()
			return "Article Approuve"
	
@frappe.whitelist()
def en_cours_item(item_code):
	if item_code:
		item = frappe.get_doc("Supplier Quotation Item",item_code)
		if item:
			
			item.confirmation = "En cours"
			item.save()
			frappe.db.set_value("Supplier Quotation", item.parent, "etat_mail", "Email Non Envoye")
			sq = frappe.get_doc("Supplier Quotation",item.parent)
			if sq:
				sq.set_resultat()
			return "Article En cours"
		
@frappe.whitelist()
def annuler_item(item_code):
	if item_code:
		item = frappe.get_doc("Supplier Quotation Item",item_code)
		if item:
			
			item.confirmation = "Annule"
			item.rate = item.prix_fournisseur
			item.qty = 0
			item.save()
			frappe.db.set_value("Supplier Quotation", item.parent, "etat_mail", "Email Non Envoye")
			sq = frappe.get_doc("Supplier Quotation",item.parent)
			if sq:
				sq.set_resultat()
			return "Article Annule"
#negociation_item
@frappe.whitelist()
def negociation_item(item_code):
	if item_code:
		item = frappe.get_doc("Supplier Quotation Item",item_code)
		if item:
			if not item.qts_target and not item.prix_target:
				return "Il faut mettre le prix et qts target avant de modifier le status!"
			item.confirmation = "En negociation"
			
			#item.etat_mail = "Email Non Envoye"
			#item.rate = item.prix_fournisseur
			#item.qty = 0
			item.save()
			frappe.db.set_value("Supplier Quotation", item.parent, "etat_mail", "Email Non Envoye")
			sq = frappe.get_doc("Supplier Quotation",item.parent)
			if sq:
				sq.set_resultat()
			return "Article Annule"
@frappe.whitelist()
def prix_target_item(item_code,qty):
	if item_code and qty:
		item = frappe.get_doc("Supplier Quotation Item",item_code)
		if item:
			item.prix_target = float(qty)
			nego = 0
			if item.qts_target > 0 and item.prix_target > 0:
				nego = 1
				item.confirmation = "En negociation"
				item.save()
			else:
				item.save()
			supplier_id = frappe.db.get_value("Supplier Quotation",item.parent,"supplier")
			taux_approche = frappe.db.get_value("Supplier",supplier_id,"taux_approche") or 1
			_taux_mb = frappe.db.get_value("Supplier",supplier_id,"taux_mb") or 0
			taux_mb = 0.0
			if _taux_mb and _taux_mb > 0:
				taux_mb = float(_taux_mb / 100)
			value = float(qty) * taux_approche * (1+taux_mb) * 1.19
			frappe.db.set_value("Supplier Quotation", item.parent, "etat_mail", "Email Non Envoye")
			sq = frappe.get_doc("Supplier Quotation",item.parent)
			if sq:
				sq.set_resultat()
			#if nego ==1:
			return "Nouveau prix target enregistree ! %s" % value
			#return "Il faut mettre le prix et qts target !"
	
@frappe.whitelist()
def qts_target_item(item_code,qty):
	if item_code and qty:
		item = frappe.get_doc("Supplier Quotation Item",item_code)
		if item:
			item.qts_target = float(qty)
			if item.qts_target > 0 and item.prix_target > 0:
				item.confirmation = "En negociation"
				item.save()
				return "qts target enregistree"
			item.save()
			frappe.db.set_value("Supplier Quotation", item.parent, "etat_mail", "Email Non Envoye")
			sq = frappe.get_doc("Supplier Quotation",item.parent)
			if sq:
				sq.set_resultat()
			return "Qts target enregistree, Il faut mettre le prix et qts target !"
			


@frappe.whitelist()
def remarque_item(item_code,qty):
	if item_code and qty:
		item = frappe.get_doc("Supplier Quotation Item",item_code)
		if item:
			item.remarque = qty
			item.save()
			return "remarque enregistree"

@frappe.whitelist()
def reponse_item(item_code,qty):
	if item_code and qty:
		item = frappe.get_doc("Supplier Quotation Item",item_code)
		if item:
			item.reponse_fournisseur = qty
			item.save()
			return "reponse enregistree"

@frappe.whitelist()
def commentaire_item(item_code,qty):
	if item_code and qty:
		item = frappe.get_doc("Supplier Quotation Item",item_code)
		if item:
			item.commentaire = qty
			item.save()
			return "commentaire enregistree"
