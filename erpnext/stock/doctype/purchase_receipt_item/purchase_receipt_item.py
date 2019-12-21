# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.model.document import Document
from erpnext.controllers.print_settings import print_settings_for_item_table

class PurchaseReceiptItem(Document):
        def validate(self):
            #if (not self.original_qts or self.original_qts == 0) and self.docstatus == 0:
            self.original_qts = self.qty
            self.qts_ecart = self.qty - self.original_qts
            self.montant_ecart = self.net_rate * self.qts_ecart
	def __setup__(self):
		print_settings_for_item_table(self)
