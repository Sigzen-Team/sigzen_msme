# Copyright (c) 2026, Sigzen Msme and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class MSMERegistrationDetail(Document):
	def validate(self):
		if self.to_date and self.from_date and self.to_date < self.from_date:
			frappe.throw(_("Row {0}: To Date cannot be before From Date").format(self.idx))
