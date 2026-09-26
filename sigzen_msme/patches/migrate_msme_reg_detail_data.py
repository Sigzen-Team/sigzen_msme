"""Carry existing MSME Registration Detail row data from the old field names to
the renamed columns, then drop the old columns.

Fieldname rename (source-edited in the doctype JSON):
    from_date      -> effective_from
    to_date        -> effective_to
    contract_done  -> msme_contract_done

A plain JSON rename makes Frappe add the new columns and leave the old ones as
orphans (it never auto-copies or auto-drops). This patch copies old -> new, then
drops the old columns. Guarded by the live column list, so it is idempotent.
"""

import frappe

OLD_TO_NEW = {
    "from_date": "effective_from",
    "to_date": "effective_to",
    "contract_done": "msme_contract_done",
}
TABLE = "tabMSME Registration Detail"


def execute():
    # apply the renamed schema so the new columns exist
    frappe.reload_doc("Sigzen Msme", "doctype", "msme_registration_detail")

    cols = frappe.db.get_table_columns("MSME Registration Detail")

    # 1) copy old -> new (only where both columns are present)
    sets = [f"`{new}` = `{old}`" for old, new in OLD_TO_NEW.items() if old in cols and new in cols]
    if sets:
        frappe.db.sql(f"UPDATE `{TABLE}` SET " + ", ".join(sets))

    # 2) drop the old columns last
    drops = [f"DROP COLUMN `{old}`" for old in OLD_TO_NEW if old in cols]
    if drops:
        frappe.db.sql(f"ALTER TABLE `{TABLE}` " + ", ".join(drops))
