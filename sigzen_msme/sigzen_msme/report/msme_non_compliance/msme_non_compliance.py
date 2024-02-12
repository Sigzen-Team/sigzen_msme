# Copyright (c) 2024, Sigzen Msme and contributors
# For license information, please see license.txt

import frappe
from frappe import _, qb, scrub
import datetime
from frappe.utils import *


def execute(filters=None):
    columns = [
        {"label": "Purchase ID", "fieldname": "purchase_id", "fieldtype": "Link", "options": "Purchase Invoice", "width": 200},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"label": "Supplier No", "fieldname": "supplier_no", "fieldtype": "Data", "width": 180},
        {"label": "MSME Contract Done", "fieldname": "contract_yes_no", "fieldtype": "Data", "width": 170},
    ]
    if filters.ageing_based_on == "Posting Date":
        columns.append({"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 180})
    else:
        columns.append({"label": "Supplier Invoice Date", "fieldname": "bill_date", "fieldtype": "Date", "width": 180})

    columns.extend([
        {"label": "Due Date", "fieldname": "due_date", "fieldtype": "Date", "width": 180},
        {"label": "Invoice Amount", "fieldname": "invoice_amount", "fieldtype": "Currency", "width": 180},
        {"label": "Current Outstanding", "fieldname": "outstanding", "fieldtype": "Currency", "width": 180},
        {"label": "Paid Amt Before Due Dt", "fieldname": "paid_amount_before", "fieldtype": "Currency", "width": 180},
        {"label": "Paid Amt After Due Dt", "fieldname": "paid_amount_after", "fieldtype": "Currency", "width": 180},
        {"label": "Disallowed Amount", "fieldname": "disallowed_amount", "fieldtype": "Currency","width": 180}
    ])

    

    data = get_data(filters)
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
            `tabPurchase Invoice`.base_grand_total,
            `tabPurchase Invoice`.outstanding_amount,
            `tabPurchase Invoice`.status,
            `tabPurchase Invoice`.bill_no,
            `tabPurchase Invoice`.bill_date  
        FROM
            `tabSupplier`,
            `tabPurchase Invoice`
        WHERE
            `tabPurchase Invoice`.supplier = `tabSupplier`.name AND
            `tabPurchase Invoice`.status NOT IN ('Cancelled', 'Draft', 'Return', 'Debit Note Issued') AND
            `tabPurchase Invoice`.posting_date between %(from_date)s AND %(to_date)s 
        
            
    """
    
    if filters.supplier:
        query += " AND `tabPurchase Invoice`.supplier = %(supplier)s"
    if filters.supplier_group:
        query += " AND `tabSupplier`.supplier_group = %(supplier_group)s"
    if filters.custom_msme_type:
        query += " AND `tabSupplier`.custom_msme_type = %(custom_msme_type)s"
    if filters.custom_contract_done:
        query += " AND `tabSupplier`.custom_contract_done = %(custom_contract_done)s"
    
    
    purchase_invoices = frappe.db.sql(query+"GROUP BY `tabPurchase Invoice`.name", {'supplier': filters.supplier, 'supplier_group': filters.supplier_group,'custom_msme_type': filters.custom_msme_type,'custom_contract_done': filters.custom_contract_done,'from_date':filters.from_date,'to_date':filters.to_date}, as_dict=True)

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

        for entry in payment_entries:
            posting_date = entry.get("posting_date")

            if posting_date > due_date:
                paid_amount_after += entry.get("paid_amount")
                disallowed_amount += entry.get("paid_amount")  
            else:
                paid_amount_before += entry.get("paid_amount")  

        if invoice.custom_msme_registered == "Yes" and invoice.base_grand_total != paid_amount_before and invoice.custom_msme_type != "Medium":
            row = {
                'purchase_id': invoice.name,
                'supplier': invoice.supplier,
                'invoice_amount': invoice.base_grand_total,
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



def get_fiscal_year_dates(fiscal_year):
   
    fiscal_year_start_date = datetime.datetime(fiscal_year - 1, 4, 1)
    print(fiscal_year_start_date)
    fiscal_year_end_date = datetime.datetime(fiscal_year, 3, 31)
    return fiscal_year_start_date, fiscal_year_end_date
