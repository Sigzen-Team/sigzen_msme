import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import  make_property_setter
from sigzen_msme.constants.custom_fields import b 




b= {
    "Supplier": [
        {
            "fieldname": "custom_msme_registered",
            "fieldtype": "Select",
            "options" : "\nYes\nNo",
            "reqd": 1,
            "insert_after": "country",
            "label": "MSME Registered",
            "is_system_generated": 1
        },
        {
        
            "fieldname": "custom_msme_registration_no",
            "depends_on": "eval:doc.custom_msme_registered== 'Yes'",
            "mandatory_depends_on": "eval:doc.custom_msme_registered=='Yes'",
            "fieldtype": "Data",
            "insert_after": "is_transporter",
            "label": "MSME Registration No",
            "is_system_generated": 0
        },
        {
        
            "fieldname": "custom_msme_type",
            "fieldtype": "Select",
            "options" : "\nMicro\nSmall\nMedium",
            "depends_on": "eval:doc.custom_msme_registered=='Yes'",
            "mandatory_depends_on": "eval:doc.custom_msme_registered=='Yes'",
            "insert_after": "custom_msme_registered",
            "label": "MSME Type",
            "is_system_generated": 0
        },
        {
        
            "fieldname": "custom_contract_done",
            "depends_on": "eval:doc.custom_msme_registered== 'Yes'",
            "mandatory_depends_on": "eval:doc.custom_msme_registered=='Yes'",
            "fieldtype": "Select",
            "options" :  "\nYes\nNo",
            "insert_after": "custom_msme_registration_no",
            "label": "MSME Contract Done",
            "is_system_generated": 0
        },
    ]
}

def execute():
    create_custom_fields(b)
   