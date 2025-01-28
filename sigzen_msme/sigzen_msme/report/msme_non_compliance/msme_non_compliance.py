# Copyright (c) 2024, Sigzen Msme and contributors
# For license information, please see license.txt

import frappe
from frappe import _, qb
from frappe.utils import getdate
import datetime
from datetime import date

def execute(filters=None):
    """
    Main function to execute the report and return columns and data
    """
    data = get_data(filters)
    columns = get_columns(filters)
    return columns, data


def get_columns(filters):
    """
    Define the columns for the report
    """
    columns = [
        {"fieldname": "purchase_id", "label": _("Purchase ID"), "fieldtype": "Link", "options": "Purchase Invoice", "width": 200},
        {"fieldname": "supplier", "label": _("Supplier"), "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"fieldname": "supplier_no", "label": _("Supplier No"), "fieldtype": "Data", "width": 180},
        {"fieldname": "contract_yes_no", "label": _("MSME Contract Done"), "fieldtype": "Data", "width": 170},
    ]

    if filters.ageing_based_on == "Posting Date":
        columns.append({"fieldname": "posting_date", "label": _("Posting Date"), "fieldtype": "Date", "width": 180})
    else:
        columns.append({"fieldname": "bill_date", "label": _("Supplier Invoice Date"), "fieldtype": "Date", "width": 180})

    columns.extend([
        {"fieldname": "due_date", "label": _("Due Date"), "fieldtype": "Date", "width": 180},
        {"fieldname": "days_difference", "label": _("Days Difference"), "fieldtype": "Data", "width": 130},
        {"fieldname": "invoice_amount", "label": _("Invoice Amount"), "fieldtype": "Currency", "width": 180},
        {"fieldname": "outstanding", "label": _("Current Outstanding"), "fieldtype": "Currency", "width": 180},
        {"fieldname": "paid_amount_before", "label": _("Paid Amt Before Due Dt"), "fieldtype": "Currency", "width": 180},
        {"fieldname": "paid_amount_after", "label": _("Paid Amt After Due Dt"), "fieldtype": "Currency", "width": 180},
        {"fieldname": "disallowed_amount", "label": _("Disallowed Amount"), "fieldtype": "Currency", "width": 180},
        {"fieldname": "interest", "label": _("Interest Amount"), "fieldtype": "Currency", "width": 180}
    ])
    return columns

from frappe.query_builder import DocType

def get_data(filters):
    data = []
    from_date = getdate(filters.from_date) if isinstance(filters.from_date, str) else filters.from_date
    to_date = getdate(filters.to_date) if isinstance(filters.to_date, str) else filters.to_date

    # Define DocTypes
    PurchaseInvoice = DocType('Purchase Invoice')
    Supplier = DocType('Supplier')
    MSMEDetails = DocType('MSME Details')

    # Fetch Purchase Invoice data
    query = (
        frappe.qb.from_(PurchaseInvoice)
        .join(Supplier)
        .on(PurchaseInvoice.supplier == Supplier.name)
        .select(
            PurchaseInvoice.name.as_('purchase_id'),
            Supplier.name.as_('supplier'),
            PurchaseInvoice.posting_date,
            PurchaseInvoice.base_rounded_total.as_('invoice_amount'),
            PurchaseInvoice.outstanding_amount.as_('outstanding'),
            PurchaseInvoice.status,
            PurchaseInvoice.bill_no.as_('supplier_no'),
            PurchaseInvoice.bill_date
        )
        .where(
            (PurchaseInvoice.posting_date.between(from_date, to_date)) &
            (PurchaseInvoice.status.notin(['Cancelled', 'Draft', 'Return', 'Debit Note Issued']))
        )
    )
    
    if filters.supplier:
        query = query.where(PurchaseInvoice.supplier == filters.supplier)
    if filters.supplier_group:
        query = query.where(Supplier.supplier_group == filters.supplier_group)

    purchase_invoice_data = query.run(as_dict=True)

    # Fetch MSME Details
    msme_details_query = frappe.qb.from_(MSMEDetails).select(
        MSMEDetails.msme_registered,
        MSMEDetails.msme_registration_no,
        MSMEDetails.msme_type,
        MSMEDetails.msme_contract_done,
        MSMEDetails.effective_from,
        MSMEDetails.effective_to,
        MSMEDetails.parent
    )
    if filters.supplier:
        msme_details_query = msme_details_query.where(MSMEDetails.parent == filters.supplier)
    if filters.custom_msme_type:
        msme_details_query = msme_details_query.where(MSMEDetails.msme_type == filters.custom_msme_type)
    if filters.custom_contract_done:
        msme_details_query = msme_details_query.where(MSMEDetails.msme_contract_done == filters.custom_contract_done)

    msme_details_data = msme_details_query.run(as_dict=True)

    msme_settings = frappe.get_doc('MSME Settings')
    yes = msme_settings.get('yes')
    no = msme_settings.get('no')
    interest = msme_settings.get('interest')

    # Match and avoid duplicates
    for pi in purchase_invoice_data:
        matched = False
        for msme in msme_details_data:
            
            # Check if the invoice's posting date falls within the MSME's effective date range
            if msme['effective_from'] and msme['effective_to'] and pi['posting_date']:
                if pi['posting_date'] >= msme['effective_from'] and pi['posting_date'] <= msme['effective_to']:
                    if not matched:  # Avoid duplicate entries
                        contract_day = msme.get('msme_contract_done')
                        due_date = calculate_due_date(pi, filters, yes, no, contract_day)
                        paid_amount_before, paid_amount_after, disallowed_amount = calculate_payments(pi, due_date)

                        if due_date < datetime.date.today() and paid_amount_after == 0:
                            disallowed_amount += pi.get('outstanding', 0)
                        
                        interest_calculation = disallowed_amount * (interest / 100) if disallowed_amount > 0 else 0

                        if msme['msme_registered'] == "Yes" and pi.get('invoice_amount') != paid_amount_before and msme['msme_type'] != "Medium":
                            days_difference = (date.today() - due_date).days if due_date else None
                            data.append({
                                'purchase_id': pi.get('purchase_id'),
                                'supplier': pi.get('supplier'),
                                'invoice_amount': pi.get('invoice_amount'),
                                'contract_yes_no': contract_day,
                                'posting_date': pi.get('posting_date'),
                                'due_date': due_date,
                                'days_difference': days_difference,
                                'bill_date': pi.get('bill_date'),
                                'paid_amount_after': paid_amount_after,
                                'paid_amount_before': paid_amount_before,
                                'outstanding': pi.get('outstanding'),
                                'supplier_no': pi.get('supplier_no'),
                                'disallowed_amount': disallowed_amount,
                                'interest': interest_calculation
                            })
                        matched = True 
    return data


def calculate_due_date(invoice, filters, yes, no, contract_day):
    """
    Calculate the due date based on contract status and ageing basis
    """
    days = yes if contract_day == "Yes" else no
    date_field = invoice.posting_date or invoice.bill_date if filters.ageing_based_on == "Posting Date" else invoice.bill_date or invoice.posting_date

    if date_field:  
        return date_field + datetime.timedelta(days=days - 1)
    
    return None


def calculate_payments(invoice, due_date):
    """
    Calculate the payments before and after due date
    """
    paid_amount_before = paid_amount_after = disallowed_amount = 0
    payment_entries = frappe.get_all("Payment Entry", filters={"reference_name": invoice.get("purchase_id")}, fields=["posting_date", "paid_amount"])
    journal_entries = frappe.get_all("Journal Entry", filters={"reference_name": invoice.get("purchase_id")}, fields=["posting_date", "total_debit"])

    for entry in payment_entries + journal_entries:
        posting_date = entry.get("posting_date")
        amount = entry.get("paid_amount", 0) or entry.get("total_debit", 0)

        if posting_date > due_date:
            paid_amount_after += amount
            disallowed_amount += amount  
        else:
            paid_amount_before += amount

    return paid_amount_before, paid_amount_after, disallowed_amount
