import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from sigzen_msme.constants.custom_fields import custom_fields


def after_install():
    # update=True so after_migrate re-asserts the canonical field defs every run
    # (e.g. keeps Address/Supplier custom_msme_details -> "MSME Registration Detail").
    create_custom_fields(custom_fields, update=True)
