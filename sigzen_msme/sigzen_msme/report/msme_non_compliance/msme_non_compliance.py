# Copyright (c) 2024, Sigzen Msme and contributors
# For license information, please see license.txt

from erpnext.accounts.doctype import journal_entry
import frappe
from frappe import _, qb, scrub
import datetime
from frappe.utils import *


def execute(filters=None):
    data = get_data(filters)

    columns = [
        {
            "fieldname": "purchase_id",
            "label": _("Purchase ID"),
            "fieldtype": "Link",
            "options": "Purchase Invoice",
            "width": 200
        },
        {
            "fieldname": "supplier",
            "label": _("Supplier"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 180
        },
        {
            "fieldname": "supplier_no",
            "label": _("Supplier No"),
            "fieldtype": "Data",
            "width": 180
        },
        {
            "fieldname": "contract_yes_no",
            "label": _("MSME Contract Done"),
            "fieldtype": "Data",
            "width": 170
        }
    ]

    if filters.ageing_based_on == "Posting Date":
        columns.append({
            "fieldname": "posting_date",
            "label": _("Posting Date"),
            "fieldtype": "Date",
            "width": 180
        })
    else:
        columns.append({
            "fieldname": "bill_date",
            "label": _("Supplier Invoice Date"),
            "fieldtype": "Date",
            "width": 180
        })

    columns.extend([
        {
            "fieldname": "due_date",
            "label": _("Due Date"),
            "fieldtype": "Date",
            "width": 180
        },
        {
            "fieldname": "invoice_amount",
            "label": _("Invoice Amount"),
            "fieldtype": "Currency",
            "width": 180
        },
        {
            "fieldname": "outstanding",
            "label": _("Current Outstanding"),
            "fieldtype": "Currency",
            "width": 180
        },
        {
            "fieldname": "paid_amount_before",
            "label": _("Paid Amt Before Due Dt"),
            "fieldtype": "Currency",
            "width": 180
        },
        {
            "fieldname": "paid_amount_after",
            "label": _("Paid Amt After Due Dt"),
            "fieldtype": "Currency",
            "width": 180
        },
        {
            "fieldname": "disallowed_amount",
            "label": _("Disallowed Amount"),
            "fieldtype": "Currency",
            "width": 180
        }
    ])
    return columns, data

def get_data(filters):
    data = []
   
  
    query = """
        SELECT 
            `tabPurchase Invoice`.name,
            `tabSupplier`.name as supplier,
            `tabSupplier`.custom_contract_done,
            `tabSupplier`.custom_msme_registered,
            `tabSupplier`.custom_msme_type,
            `tabPurchase Invoice`.posting_date,
            `tabPurchase Invoice`.base_rounded_total,
            `tabPurchase Invoice`.outstanding_amount,
            `tabPurchase Invoice`.status,
            `tabPurchase Invoice`.bill_no,
            `tabPurchase Invoice`.bill_date  
        FROM
            `tabSupplier`,
            `tabPurchase Invoice`
        WHERE
            `tabPurchase Invoice`.posting_date between %(from_date)s AND %(to_date)s AND
            `tabPurchase Invoice`.supplier = `tabSupplier`.name AND
            `tabPurchase Invoice`.status NOT IN ('Cancelled', 'Draft', 'Return', 'Debit Note Issued')
            
        
            
    """
    
    if filters.supplier:
        query += " AND `tabPurchase Invoice`.supplier = %(supplier)s"
    if filters.supplier_group:
        query += " AND `tabSupplier`.supplier_group = %(supplier_group)s"
    if filters.custom_msme_type:
        query += " AND `tabSupplier`.custom_msme_type = %(custom_msme_type)s"
    if filters.custom_contract_done:
        query += " AND `tabSupplier`.custom_contract_done = %(custom_contract_done)s"
    
    
    purchase_invoices = frappe.db.sql(query+"GROUP BY `tabPurchase Invoice`.name", {'supplier': filters.supplier, 'supplier_group': filters.supplier_group,'custom_msme_type': filters.custom_msme_type,'custom_contract_done': filters.custom_contract_done,'from_date':filters.from_date,'to_date':filters.to_date}, as_dict=True)#// nosemgrep

    msme_settings = frappe.get_doc('MSME Settings')
    yes = msme_settings.get('yes')
    no = msme_settings.get('no')
    

    for invoice in purchase_invoices:
        if invoice.custom_contract_done == "Yes":
            if filters.ageing_based_on == "Posting Date":
                if invoice.posting_date:
                    due_date = (invoice.posting_date - datetime.timedelta(1)) + datetime.timedelta(days=yes)
                elif invoice.bill_date:
                    due_date = (invoice.bill_date - datetime.timedelta(1)) + datetime.timedelta(days=yes)
            elif filters.ageing_based_on == "Supplier Invoice Date":
                if invoice.bill_date:
                    due_date = (invoice.bill_date - datetime.timedelta(1)) + datetime.timedelta(days=yes)
                elif invoice.posting_date:
                    due_date = (invoice.posting_date - datetime.timedelta(1)) + datetime.timedelta(days=yes)
        else:
            if filters.ageing_based_on == "Posting Date":
                if invoice.posting_date:
                    due_date = (invoice.posting_date - datetime.timedelta(1)) + datetime.timedelta(days=no)
                elif invoice.bill_date:
                    due_date = (invoice.bill_date - datetime.timedelta(1)) + datetime.timedelta(days=no)
            elif filters.ageing_based_on == "Supplier Invoice Date":
                if invoice.bill_date:
                    due_date = (invoice.bill_date - datetime.timedelta(1)) + datetime.timedelta(days=no)
                elif invoice.posting_date:
                    due_date = (invoice.posting_date - datetime.timedelta(1)) + datetime.timedelta(days=no)

        paid_amount_after = 0
        paid_amount_before = 0
        disallowed_amount = 0

        payment_entries = frappe.get_all("Payment Entry", filters={"reference_name": invoice.name}, fields=["posting_date","paid_amount"])
        journal_entry = frappe.get_all("Journal Entry", filters={"reference_name": invoice.name}, fields=["posting_date","total_debit"])
        if payment_entries:
            for entry in payment_entries:
                posting_date = entry.get("posting_date")

                if posting_date > due_date:
                    paid_amount_after += entry.get("paid_amount")
                    disallowed_amount += entry.get("paid_amount")  
                else:
                    paid_amount_before += entry.get("paid_amount")
        else:
            for entry in journal_entry:
                posting_date = entry.get("posting_date")

                if posting_date > due_date:
                    paid_amount_after += entry.get("total_debit")
                    disallowed_amount += entry.get("total_debit")  
                else:
                    paid_amount_before += entry.get("total_debit")  

        if invoice.custom_msme_registered == "Yes" and invoice.base_rounded_total != paid_amount_before and invoice.custom_msme_type != "Medium":
            row = {
                'purchase_id': invoice.name,
                'supplier': invoice.supplier,
                'invoice_amount': invoice.base_rounded_total,
                'contract_yes_no': invoice.custom_contract_done,
                'posting_date': invoice.posting_date,
                'due_date': due_date,
                'bill_date': invoice.bill_date,
                'paid_amount_after': paid_amount_after,
                'paid_amount_before': paid_amount_before,
                'outstanding': invoice.outstanding_amount,
                'supplier_no': invoice.bill_no,
                'disallowed_amount': disallowed_amount 
            }
            data.append(row)

    return data

