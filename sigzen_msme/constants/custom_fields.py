# All custom fields owned by sigzen_msme.
# Every dict carries "module": "Sigzen Msme" so uninstall.py can delete them by module.
#
# NOTE (Phase 4): the 4 legacy flat Supplier fields below
#   (custom_msme_registered / custom_msme_registration_no /
#    custom_msme_type / custom_contract_done)
# are removed by patch `remove_flat_msme_fields`. When that patch is enabled,
# DELETE those 4 dicts from this file too -- otherwise after_migrate's
# create_custom_fields re-creates them.

MODULE = "Sigzen Msme"

custom_fields = {
    "Supplier": [
        {
            "fieldname": "custom_msme_details_tab",
            "fieldtype": "Tab Break",
            "label": "MSME Details",
            "insert_after": "customer_numbers",
            "module": MODULE,
        },
        {
            "fieldname": "custom_msme_details",
            "fieldtype": "Table",
            "options": "MSME Registration Detail",
            "label": "MSME Registration Details",
            "insert_after": "custom_msme_details_tab",
            "module": MODULE,
        },
    ],
    "Address": [
        {
            "fieldname": "custom_license_details_tab",
            "fieldtype": "Tab Break",
            "label": "License Details",
            "insert_after": "links",
            "module": MODULE,
        },
        {
            "fieldname": "custom_msme_details",
            "fieldtype": "Table",
            "options": "MSME Registration Detail",
            "label": "MSME Registration Details",
            "insert_after": "custom_license_details_tab",
            "module": MODULE,
        },
    ],
}

# Backwards-compatible alias (old code imported `b`)
b = custom_fields
