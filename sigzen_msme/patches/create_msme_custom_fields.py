"""Create the MSME custom fields on an already-installed site.

On a fresh install the after_install hook creates them; on existing sites the
after_migrate hook does -- but that hook runs AFTER post_model_sync patches, so
this patch guarantees the child DocType + custom fields exist before the
backfill patch runs.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from sigzen_msme.constants.custom_fields import custom_fields


def execute():
    frappe.reload_doc("Sigzen Msme", "doctype", "msme_registration_detail")
    create_custom_fields(custom_fields, update=True)
