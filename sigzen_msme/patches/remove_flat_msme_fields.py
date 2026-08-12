"""PHASE 4 -- remove the legacy flat MSME custom fields from Supplier once the
child table (MSME Registration Detail) is backfilled and the report reads it.

DO NOT enable in patches.txt until:
  1. `backfill_msme_details` has run and been verified, AND
  2. the 4 flat field dicts are DELETED from constants/custom_fields.py
     (else after_migrate's create_custom_fields re-creates them).
"""

import frappe

FLAT_FIELDS = [
    ("Supplier", "custom_msme_registered"),
    ("Supplier", "custom_msme_registration_no"),
    ("Supplier", "custom_msme_type"),
    ("Supplier", "custom_contract_done"),
]


def execute():
    for dt, fn in FLAT_FIELDS:
        name = frappe.db.get_value("Custom Field", {"dt": dt, "fieldname": fn})
        if name:
            frappe.delete_doc("Custom Field", name, ignore_permissions=True, force=True)
    frappe.clear_cache(doctype="Supplier")
