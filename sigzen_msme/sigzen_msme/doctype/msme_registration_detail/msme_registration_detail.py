# Copyright (c) 2026, Sigzen Msme and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class MSMERegistrationDetail(Document):
	def validate(self):
		if self.effective_to and self.effective_from and self.effective_to < self.effective_from:
			frappe.throw(_("Row {0}: Effective To cannot be before Effective From").format(self.idx))
