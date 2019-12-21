# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class Manufacturer(Document):
	def validate(self):
		if not self.code:
			code = frappe.db.sql("""SELECT Count(*) FROM tabManufacturer""")[0][0] + 1
			if len(str(code)) < 3:
				ncode = str(code).rjust(3,str('0'))
			self.code = ncode
			#self.code = make_autoname(".###",'Manufacturer') 	
