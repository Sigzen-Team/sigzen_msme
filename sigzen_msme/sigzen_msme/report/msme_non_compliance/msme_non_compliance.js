// Copyright (c) 2024, Sigzen Msme and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["MSME Non-Compliance"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"reqd": 1,
			"on_change": function(query_report) {
				// Get the fiscal year value
				var fiscal_year = query_report.get_values().fiscal_year;
				if (!fiscal_year) {
					return;
				}
				
				// Fetch fiscal year document and set from_date and to_date filters
				frappe.model.with_doc("Fiscal Year", fiscal_year, function(r) {
					var fy = frappe.model.get_doc("Fiscal Year", fiscal_year);
					frappe.query_report.set_filter_value({
						from_date: fy.year_start_date,
						to_date: fy.year_end_date
					});
				});
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_start_date"),
			
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_end_date"),
			
		},
		{
			"fieldname": "supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
		},
		{
			"fieldname": "supplier_group",
			"label": __("Supplier Group"),
			"fieldtype": "Link",
			"options": "Supplier Group",
		},
		{
			"fieldname": "ageing_based_on",
			"label": __("Ageing Based On"),
			"fieldtype": "Select",
			"options": 'Posting Date\nSupplier Invoice Date',
			"default": "Posting Date"
		},
		{
			"fieldname": "custom_msme_type",
			"label": __("MSME Type"),
			"fieldtype": "Select",
			"options": '\nMicro\nSmall\nMedium',
			
		},
		{
			"fieldname": "custom_contract_done",
			"label": __("MSME Contract Done"),
			"fieldtype": "Select",
			"options": '\nYes\nNo',
			
		}
	]
};
