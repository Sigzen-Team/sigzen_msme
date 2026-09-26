# Copyright (c) 2024, Sigzen Msme and contributors
# For license information, please see license.txt

import datetime

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.utils import cint, flt, getdate, nowdate

CHILD_FIELD = "custom_msme_details"


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    columns = [
        {"fieldname": "purchase_id", "label": _("Purchase ID"), "fieldtype": "Link", "options": "Purchase Invoice", "width": 200},
        {"fieldname": "supplier", "label": _("Supplier"), "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"fieldname": "supplier_no", "label": _("Supplier No"), "fieldtype": "Data", "width": 180},
        {"fieldname": "contract_yes_no", "label": _("MSME Contract Done"), "fieldtype": "Data", "width": 170},
    ]

    if filters.get("ageing_based_on") == "Posting Date":
        columns.append({"fieldname": "posting_date", "label": _("Posting Date"), "fieldtype": "Date", "width": 180})
    else:
        columns.append({"fieldname": "bill_date", "label": _("Supplier Invoice Date"), "fieldtype": "Date", "width": 180})

    columns.extend([
        {"fieldname": "due_date", "label": _("Due Date"), "fieldtype": "Date", "width": 180},
        {"fieldname": "invoice_amount", "label": _("Invoice Amount"), "fieldtype": "Currency", "width": 180},
        {"fieldname": "outstanding", "label": _("Current Outstanding"), "fieldtype": "Currency", "width": 180},
        {"fieldname": "paid_amount_before", "label": _("Paid Amt Before Due Dt"), "fieldtype": "Currency", "width": 180},
        {"fieldname": "paid_amount_after", "label": _("Paid Amt After Due Dt"), "fieldtype": "Currency", "width": 180},
        {"fieldname": "disallowed_amount", "label": _("Disallowed Amount"), "fieldtype": "Currency", "width": 180},
        {"fieldname": "interest", "label": _("Interest Amount"), "fieldtype": "Currency", "width": 180},
    ])
    return columns


def get_data(filters):
    filters = filters or frappe._dict()

    source = frappe.db.get_single_value("MSME Settings", "msme_detail_source") or "Supplier"
    yes_days = cint(frappe.db.get_single_value("MSME Settings", "yes"))
    no_days = cint(frappe.db.get_single_value("MSME Settings", "no"))
    interest_pct = flt(frappe.db.get_single_value("MSME Settings", "interest"))

    PI = DocType("Purchase Invoice")
    S = DocType("Supplier")

    query = (
        frappe.qb.from_(PI)
        .join(S)
        .on(PI.supplier == S.name)
        .select(
            PI.name,
            S.name.as_("supplier"),
            PI.supplier_address,
            PI.posting_date,
            PI.base_rounded_total,
            PI.outstanding_amount,
            PI.status,
            PI.bill_no,
            PI.bill_date,
        )
        .where(
            (PI.posting_date.between(filters.from_date, filters.to_date))
            & (PI.docstatus == 1)
            & (PI.status.notin(["Cancelled", "Draft", "Return", "Debit Note Issued"]))
        )
    )

    if filters.get("company"):
        query = query.where(PI.company == filters.company)
    if filters.get("supplier"):
        query = query.where(PI.supplier == filters.supplier)
    if filters.get("supplier_group"):
        query = query.where(S.supplier_group == filters.supplier_group)

    invoices = query.run(as_dict=True)

    cache = {}
    data = []
    for inv in invoices:
        reg = resolve_registration(inv, source, cache)

        # only registered Micro/Small suppliers are in scope (Medium is exempt)
        if not reg or reg.get("msme_registered") != "Yes":
            continue
        if reg.get("msme_type") == "Medium":
            continue

        # filters now apply to the resolved registration row
        if filters.get("custom_msme_type") and reg.get("msme_type") != filters.custom_msme_type:
            continue
        if filters.get("custom_contract_done") and reg.get("msme_contract_done") != filters.custom_contract_done:
            continue

        due_date = calculate_due_date(inv, filters, reg.get("msme_contract_done"), yes_days, no_days)
        if not due_date:
            continue

        paid_before, paid_after, disallowed = calculate_payments(inv, due_date)

        if due_date < getdate(nowdate()) and paid_after == 0:
            disallowed += flt(inv.outstanding_amount)

        interest_amount = disallowed * interest_pct / 100 if disallowed > 0 else 0

        if flt(inv.base_rounded_total) != paid_before:
            data.append({
                "purchase_id": inv.name,
                "supplier": inv.supplier,
                "invoice_amount": inv.base_rounded_total,
                "contract_yes_no": reg.get("msme_contract_done"),
                "posting_date": inv.posting_date,
                "due_date": due_date,
                "bill_date": inv.bill_date,
                "paid_amount_after": paid_after,
                "paid_amount_before": paid_before,
                "outstanding": inv.outstanding_amount,
                "supplier_no": inv.bill_no,
                "disallowed_amount": disallowed,
                "interest": interest_amount,
            })

    return data


def resolve_registration(inv, source, cache):
    """Return the MSME Registration Detail row effective on the invoice date.

    O4: source == "Address" -> Purchase Invoice.supplier_address, else supplier
    primary Address, else fall back to the Supplier's own rows.
    O3: among rows valid on the invoice date, the latest effective_from wins.
    """
    invoice_date = getdate(inv.posting_date or inv.bill_date)

    parents = []
    if source == "Address":
        addr = inv.supplier_address or get_primary_address(inv.supplier, cache)
        if addr:
            parents.append(("Address", addr))
        parents.append(("Supplier", inv.supplier))  # graceful fallback
    else:
        parents.append(("Supplier", inv.supplier))

    for parenttype, parent in parents:
        rows = get_registration_rows(parenttype, parent, cache)
        effective = pick_effective_row(rows, invoice_date)
        if effective:
            return effective
    return None


def pick_effective_row(rows, invoice_date):
    eligible = [
        r for r in rows
        if r.effective_from
        and getdate(r.effective_from) <= invoice_date
        and (not r.effective_to or getdate(r.effective_to) >= invoice_date)
    ]
    if not eligible:
        return None
    # latest effective_from wins; tie -> highest idx
    eligible.sort(key=lambda r: (getdate(r.effective_from), r.idx))
    return eligible[-1]


def get_registration_rows(parenttype, parent, cache):
    key = ("rows", parenttype, parent)
    if key not in cache:
        cache[key] = frappe.get_all(
            "MSME Registration Detail",
            filters={"parenttype": parenttype, "parent": parent, "parentfield": CHILD_FIELD},
            fields=["effective_from", "effective_to", "msme_registered", "msme_type", "msme_contract_done", "idx"],
        )
    return cache[key]


def get_primary_address(supplier, cache):
    key = ("addr", supplier)
    if key not in cache:
        addrs = frappe.get_all(
            "Address",
            filters=[
                ["Dynamic Link", "link_doctype", "=", "Supplier"],
                ["Dynamic Link", "link_name", "=", supplier],
            ],
            fields=["name", "is_primary_address"],
            order_by="is_primary_address desc, `tabAddress`.creation asc",
        )
        cache[key] = addrs[0].name if addrs else None
    return cache[key]


def calculate_due_date(inv, filters, contract_done, yes_days, no_days):
    days = yes_days if contract_done == "Yes" else no_days
    if filters.get("ageing_based_on") == "Posting Date":
        base = inv.posting_date or inv.bill_date
    else:
        base = inv.bill_date or inv.posting_date

    if base:
        return (getdate(base) - datetime.timedelta(1)) + datetime.timedelta(days=cint(days))
    return None


def calculate_payments(inv, due_date):
    """Payments applied to this invoice, split before/after the due date.

    Payment/Journal references live in child tables, not the parent -- read
    Payment Entry Reference and Journal Entry Account.
    """
    paid_before = paid_after = disallowed = 0.0

    pe_refs = frappe.get_all(
        "Payment Entry Reference",
        filters={"reference_doctype": "Purchase Invoice", "reference_name": inv.name, "docstatus": 1},
        fields=["parent", "allocated_amount"],
    )
    payments = [
        {"posting_date": frappe.db.get_value("Payment Entry", r.parent, "posting_date"), "amount": r.allocated_amount}
        for r in pe_refs
    ]

    je_rows = frappe.get_all(
        "Journal Entry Account",
        filters={"reference_type": "Purchase Invoice", "reference_name": inv.name, "docstatus": 1},
        fields=["parent", "debit_in_account_currency"],
    )
    payments += [
        {"posting_date": frappe.db.get_value("Journal Entry", r.parent, "posting_date"), "amount": r.debit_in_account_currency}
        for r in je_rows
    ]

    for entry in payments:
        posting_date = entry["posting_date"]
        amount = flt(entry["amount"])
        if not posting_date:
            continue
        if getdate(posting_date) > due_date:
            paid_after += amount
            disallowed += amount
        else:
            paid_before += amount

    return paid_before, paid_after, disallowed
