# Copyright (c) 2024, Sigzen Msme and contributors
# For license information, please see license.txt

import frappe
from frappe import _, qb, scrub
from erpnext.accounts.doctype import journal_entry
from frappe.utils import *
import datetime

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
        {"fieldname": "invoice_amount", "label": _("Invoice Amount"), "fieldtype": "Currency", "width": 180},
        {"fieldname": "outstanding", "label": _("Current Outstanding"), "fieldtype": "Currency", "width": 180},
        {"fieldname": "paid_amount_before", "label": _("Paid Amt Before Due Dt"), "fieldtype": "Currency", "width": 180},
        {"fieldname": "paid_amount_after", "label": _("Paid Amt After Due Dt"), "fieldtype": "Currency", "width": 180},
        {"fieldname": "disallowed_amount", "label": _("Disallowed Amount"), "fieldtype": "Currency", "width": 180},
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

    # Match and avoid duplicates
    for pi in purchase_invoice_data:
        matched = False
        for msme in msme_details_data:
            
            # Check if the invoice's posting date falls within the MSME's effective date range
            if msme['effective_from'] and msme['effective_to'] and pi['posting_date']:
                # Ensure that the posting date is within the effective range
                if (
                    pi['posting_date'] >= msme['effective_from'] and 
                    pi['posting_date'] <= msme['effective_to']
                ):
                    # Add logic to avoid duplicate entries for the same invoice
                    if not matched:  # Prevent duplicate entries for the same invoice
                        due_date = calculate_due_date(pi, filters, yes, no)
                        paid_amount_before, paid_amount_after, disallowed_amount = calculate_payments(pi, due_date)

                        if due_date < datetime.date.today() and paid_amount_after == 0:
                            disallowed_amount += pi.get('outstanding', 0)

                        if msme['msme_registered'] == "Yes" and pi.get('invoice_amount') != paid_amount_before and msme['msme_type'] != "Medium":
                            data.append({
                                'purchase_id': pi.get('purchase_id'),
                                'supplier': pi.get('supplier'),
                                'invoice_amount': pi.get('invoice_amount'),
                                'contract_yes_no': msme.get('msme_contract_done'),
                                'posting_date': pi.get('posting_date'),
                                'due_date': due_date,
                                'bill_date': pi.get('bill_date'),
                                'paid_amount_after': paid_amount_after,
                                'paid_amount_before': paid_amount_before,
                                'outstanding': pi.get('outstanding'),
                                'supplier_no': pi.get('supplier_no'),
                                'disallowed_amount': disallowed_amount
                            })
                        matched = True  # Mark the invoice as matched to avoid duplicates       
    return data

def calculate_due_date(invoice, filters, yes, no):
    """
    Calculate the due date based on contract status and ageing basis
    """
    days = yes if invoice.custom_contract_done == "Yes" else no
    if filters.ageing_based_on == "Posting Date":
        date_field = invoice.posting_date or invoice.bill_date
    else:
        date_field = invoice.bill_date or invoice.posting_date

    if date_field:  
        return (date_field - datetime.timedelta(1)) + datetime.timedelta(days=days)
    return None

def calculate_payments(invoice, due_date):
    """
    Calculate the payments before and after due date
    """
    paid_amount_before = paid_amount_after = disallowed_amount = 0
    payment_entries = frappe.get_all("Payment Entry", filters={"reference_name": invoice.name}, fields=["posting_date", "paid_amount"])
    journal_entries = frappe.get_all("Journal Entry", filters={"reference_name": invoice.name}, fields=["posting_date", "total_debit"])

    for entry in payment_entries + journal_entries:
        posting_date = entry.get("posting_date")
        amount = entry.get("paid_amount", 0) or entry.get("total_debit", 0)

        if posting_date > due_date:
            paid_amount_after += amount
            disallowed_amount += amount  
        else:
            paid_amount_before += amount

    return paid_amount_before, paid_amount_after, disallowed_amount












# # Copyright (c) 2024, Sigzen Msme and contributors
# # For license information, please see license.txt

# import frappe
# from frappe import _, qb, scrub
# from erpnext.accounts.doctype import journal_entry
# from frappe.utils import *
# import datetime


# def execute(filters=None):
#     """
#     Main function to execute the report and return columns and data
#     """
#     data = get_data(filters)
#     columns = get_columns(filters)
#     return columns, data


# def get_columns(filters):
#     """
#     Define the columns for the report
#     """
#     columns = [
#         {
#             "fieldname": "purchase_id",
#             "label": _("Purchase ID"),
#             "fieldtype": "Link",
#             "options": "Purchase Invoice",
#             "width": 200
#         },
#         {
#             "fieldname": "supplier",
#             "label": _("Supplier"),
#             "fieldtype": "Link",
#             "options": "Supplier",
#             "width": 180
#         },
#         {
#             "fieldname": "supplier_no",
#             "label": _("Supplier No"),
#             "fieldtype": "Data",
#             "width": 180
#         },
#         {
#             "fieldname": "contract_yes_no",
#             "label": _("MSME Contract Done"),
#             "fieldtype": "Data",
#             "width": 170
#         }
#     ]

#     if filters.ageing_based_on == "Posting Date":
#         columns.append({
#             "fieldname": "posting_date",
#             "label": _("Posting Date"),
#             "fieldtype": "Date",
#             "width": 180
#         })
#     else:
#         columns.append({
#             "fieldname": "bill_date",
#             "label": _("Supplier Invoice Date"),
#             "fieldtype": "Date",
#             "width": 180
#         })

#     columns.extend([
#         {
#             "fieldname": "due_date",
#             "label": _("Due Date"),
#             "fieldtype": "Date",
#             "width": 180
#         },
#         {
#             "fieldname": "invoice_amount",
#             "label": _("Invoice Amount"),
#             "fieldtype": "Currency",
#             "width": 180
#         },
#         {
#             "fieldname": "outstanding",
#             "label": _("Current Outstanding"),
#             "fieldtype": "Currency",
#             "width": 180
#         },
#         {
#             "fieldname": "paid_amount_before",
#             "label": _("Paid Amt Before Due Dt"),
#             "fieldtype": "Currency",
#             "width": 180
#         },
#         {
#             "fieldname": "paid_amount_after",
#             "label": _("Paid Amt After Due Dt"),
#             "fieldtype": "Currency",
#             "width": 180
#         },
#         {
#             "fieldname": "disallowed_amount",
#             "label": _("Disallowed Amount"),
#             "fieldtype": "Currency",
#             "width": 180
#         }
#     ])
#     return columns

# from frappe.query_builder import DocType

# def get_data(filters):
#     """
#     Fetch data based on filters using Frappe's Query Builder
#     """
#     data = []
    
#     PurchaseInvoice = DocType('Purchase Invoice')
#     Supplier = DocType('Supplier')
    
#     query = (
#         frappe.qb.from_(PurchaseInvoice)
#         .join(Supplier)
#         .on(PurchaseInvoice.supplier == Supplier.name)
#         .select(
#             PurchaseInvoice.name,
#             Supplier.name.as_('supplier'),
#             Supplier.custom_contract_done,
#             Supplier.custom_msme_registered,
#             Supplier.custom_msme_type,
#             PurchaseInvoice.posting_date,
#             PurchaseInvoice.base_rounded_total,
#             PurchaseInvoice.outstanding_amount,
#             PurchaseInvoice.status,
#             PurchaseInvoice.bill_no,
#             PurchaseInvoice.bill_date
#         )
#         .where(
#             (PurchaseInvoice.posting_date.between(filters.from_date, filters.to_date)) &
#             (PurchaseInvoice.status.notin(['Cancelled', 'Draft', 'Return', 'Debit Note Issued']))
#         )
#     )
    
#     if filters.supplier:
#         query = query.where(PurchaseInvoice.supplier == filters.supplier)
#     if filters.supplier_group:
#         query = query.where(Supplier.supplier_group == filters.supplier_group)
#     if filters.custom_msme_type:
#         query = query.where(Supplier.custom_msme_type == filters.custom_msme_type)
#     if filters.custom_contract_done:
#         query = query.where(Supplier.custom_contract_done == filters.custom_contract_done)
    
#     purchase_invoices = query.groupby(PurchaseInvoice.name).run(as_dict=True)
    
#     msme_settings = frappe.get_doc('MSME Settings')
#     yes = msme_settings.get('yes')
#     no = msme_settings.get('no')
    
#     for invoice in purchase_invoices:
#         due_date = calculate_due_date(invoice, filters, yes, no)
#         paid_amount_before, paid_amount_after, disallowed_amount = calculate_payments(invoice, due_date)
        
#         if due_date < datetime.date.today() and paid_amount_after == 0:
#             disallowed_amount += invoice.outstanding_amount

#         if invoice.custom_msme_registered == "Yes" and invoice.base_rounded_total != paid_amount_before and invoice.custom_msme_type != "Medium":
#             row = {
#                 'purchase_id': invoice.name,
#                 'supplier': invoice.supplier,
#                 'invoice_amount': invoice.base_rounded_total,
#                 'contract_yes_no': invoice.custom_contract_done,
#                 'posting_date': invoice.posting_date,
#                 'due_date': due_date,
#                 'bill_date': invoice.bill_date,
#                 'paid_amount_after': paid_amount_after,
#                 'paid_amount_before': paid_amount_before,
#                 'outstanding': invoice.outstanding_amount,
#                 'supplier_no': invoice.bill_no,
#                 'disallowed_amount': disallowed_amount 
#             }
#             data.append(row)
    
#     return data

# def calculate_due_date(invoice, filters, yes, no):
#     """
#     Calculate the due date based on contract status and ageing basis
#     """
#     days = yes if invoice.custom_contract_done == "Yes" else no
#     if filters.ageing_based_on == "Posting Date":
#         date_field = invoice.posting_date or invoice.bill_date
#     else:
#         date_field = invoice.bill_date or invoice.posting_date

#     if date_field:
#         return (date_field - datetime.timedelta(1)) + datetime.timedelta(days=days)
#     return None

# def calculate_payments(invoice, due_date):
#     """
#     Calculate the payments before and after due date
#     """
#     paid_amount_before = paid_amount_after = disallowed_amount = 0
#     payment_entries = frappe.get_all("Payment Entry", filters={"reference_name": invoice.name}, fields=["posting_date", "paid_amount"])
#     journal_entries = frappe.get_all("Journal Entry", filters={"reference_name": invoice.name}, fields=["posting_date", "total_debit"])

#     for entry in payment_entries + journal_entries:
#         posting_date = entry.get("posting_date")
#         amount = entry.get("paid_amount", 0) or entry.get("total_debit", 0)

#         if posting_date > due_date:
#             paid_amount_after += amount
#             disallowed_amount += amount  
#         else:
#             paid_amount_before += amount

#     return paid_amount_before, paid_amount_after, disallowed_amount
