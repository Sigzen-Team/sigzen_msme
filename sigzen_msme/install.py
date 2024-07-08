import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import  make_property_setter
from sigzen_msme.constants.custom_fields import b 

def after_install():
    create_custom_fields(b)
   
