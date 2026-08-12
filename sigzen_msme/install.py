import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from sigzen_msme.constants.custom_fields import custom_fields


def after_install():
    create_custom_fields(custom_fields)
