"""Backfill the new MSME Registration Detail child table on Supplier from the
legacy flat custom fields.

effective_from for migrated rows = current fiscal year start date (TL decision O1).
Idempotent: skips any supplier that already has child rows.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.utils import nowdate

from sigzen_msme.constants.custom_fields import custom_fields


def execute():
    # make sure the child DocType + Supplier custom fields are present first
    frappe.reload_doc("Sigzen Msme", "doctype", "msme_registration_detail")
    create_custom_fields(custom_fields, update=True)

    fy_start = _current_fiscal_year_start()

    suppliers = frappe.get_all(
        "Supplier",
        filters={"custom_msme_registered": ["in", ["Yes", "No"]]},
        fields=[
            "name",
            "custom_msme_registered",
            "custom_msme_registration_no",
            "custom_msme_type",
            "custom_contract_done",
        ],
    )

    migrated = 0
    for s in suppliers:
        doc = frappe.get_doc("Supplier", s.name)
        if doc.get("custom_msme_details"):
            continue  # already migrated

        doc.append(
            "custom_msme_details",
            {
                "effective_from": fy_start,
                "msme_registered": s.custom_msme_registered,
                "msme_registration_no": s.custom_msme_registration_no,
                "msme_type": s.custom_msme_type,
                "msme_contract_done": s.custom_contract_done,
            },
        )
        doc.flags.ignore_validate = True
        doc.flags.ignore_mandatory = True
        doc.save(ignore_permissions=True)
        migrated += 1

    frappe.db.commit()
    frappe.logger().info(f"[sigzen_msme] backfilled MSME details for {migrated} supplier(s)")


def _current_fiscal_year_start():
    try:
        from erpnext.accounts.utils import get_fiscal_year

        return get_fiscal_year(nowdate())[1]
    except Exception:
        # fallback: 1 April of the current year's fiscal start
        from frappe.utils import getdate

        today = getdate(nowdate())
        year = today.year if today.month >= 4 else today.year - 1
        return getdate(f"{year}-04-01")
