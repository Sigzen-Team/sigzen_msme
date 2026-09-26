import frappe

APP_MODULE = "Sigzen Msme"


def before_uninstall():
    _delete_custom_fields()
    frappe.clear_cache()


def _delete_custom_fields():
    names = frappe.get_all("Custom Field", filters={"module": APP_MODULE}, pluck="name")
    for name in names:
        frappe.delete_doc("Custom Field", name, ignore_permissions=True, force=True)
