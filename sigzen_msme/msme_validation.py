"""Validation for the MSME Registration Detail rows on the parent (Supplier /
Address).

A child DocType's own validate() is NOT called when the parent is saved, so the
checks must run from the parent via doc_events (see hooks.py).
"""

import frappe
from frappe import _
from frappe.utils import getdate

CHILD_FIELD = "custom_msme_details"


def validate_msme_details(doc, method=None):
    # MSME is read from either the Supplier or the Address, per MSME Settings.
    # Only validate the configured source doctype (e.g. if source is "Supplier",
    # the Address save event does not run these checks).
    source = frappe.db.get_single_value("MSME Settings", "msme_detail_source") or "Supplier"
    if doc.doctype != source:
        return

    rows = doc.get(CHILD_FIELD)
    if not rows:
        return

    # 1. Effective To must not be before Effective From
    for row in rows:
        if row.effective_from and row.effective_to and getdate(row.effective_to) < getdate(row.effective_from):
            frappe.throw(_("Row {0}: Effective To cannot be before Effective From").format(row.idx))

    # 2. The same MSME Registration No must not carry conflicting MSME Types over
    #    overlapping / identical effective date ranges (e.g. the same number
    #    classified as both 'Micro' and 'Small' for the same active period).
    by_reg = {}
    for row in rows:
        reg = (row.msme_registration_no or "").strip()
        if reg:
            by_reg.setdefault(reg, []).append(row)

    for reg, group in by_reg.items():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]

                # Exact duplicate: same registration no + same MSME Type + same
                # effective period (same duration) -- the same fact entered twice.
                if (a.msme_type or "") == (b.msme_type or "") and _same_period(a, b):
                    frappe.throw(
                        _(
                            "Row {0}: duplicate MSME entry -- MSME Registration No {1} with the same "
                            "MSME Type and the same effective dates already exists in row {2}."
                        ).format(b.idx, frappe.bold(reg), a.idx)
                    )

                # Contradiction: overlapping effective dates with different MSME Types.
                if (
                    a.msme_type
                    and b.msme_type
                    and a.msme_type != b.msme_type
                    and _ranges_overlap(a, b)
                ):
                    frappe.throw(
                        _(
                            "MSME Registration No {0}: conflicting MSME Types over the same period "
                            "({1} in row {2} vs {3} in row {4}). The same registration number cannot be "
                            "classified under two MSME Types for overlapping effective dates."
                        ).format(frappe.bold(reg), a.msme_type, a.idx, b.msme_type, b.idx)
                    )


def _same_period(a, b):
    """True if both rows have identical Effective From and Effective To."""
    af = getdate(a.effective_from) if a.effective_from else None
    at = getdate(a.effective_to) if a.effective_to else None
    bf = getdate(b.effective_from) if b.effective_from else None
    bt = getdate(b.effective_to) if b.effective_to else None
    return af == bf and at == bt


def _ranges_overlap(a, b):
    """True if [effective_from, effective_to] of a and b overlap (or are identical).

    A missing Effective To is treated as open-ended (ongoing).
    """
    a_from = getdate(a.effective_from) if a.effective_from else None
    a_to = getdate(a.effective_to) if a.effective_to else None
    b_from = getdate(b.effective_from) if b.effective_from else None
    b_to = getdate(b.effective_to) if b.effective_to else None

    start_ok = a_from is None or b_to is None or a_from <= b_to
    end_ok = b_from is None or a_to is None or b_from <= a_to
    return start_ok and end_ok
