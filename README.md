# Sigzen MSME

Track MSME registration of your suppliers in ERPNext and find purchase invoices paid after the MSME time limit, with the amount disallowed under Section 43B(h) of the Income Tax Act and the interest payable under the MSMED Act, 2006.

## Features

- MSME registration history: one row per period on the Supplier (or Address) with Udyam number, MSME type (Micro / Small / Medium), contract yes/no, and Effective From / To dates.
- Payment terms: payable days with contract (up to 45) and without contract (15), set in MSME Settings.
- MSME Non-Compliance report: invoices from Micro and Small suppliers not fully paid by the due date, with amounts paid before and after it, the disallowed amount and interest.
- Date-aware: uses the MSME details valid on the invoice date, so a change from Micro to Small mid-year is handled.
- Validation: blocks duplicate rows and the same Udyam number with two MSME types for overlapping dates.

## Installation

Prerequisites: Frappe and ERPNext (v15 or v16) installed on your bench.

### Steps

1. Get the app:

   ```bash
   bench get-app https://github.com/Sigzen-Team/sigzen_msme.git
   ```

2. Install the app on your site:

   ```bash
   bench --site your-site install-app sigzen_msme
   ```

3. Run migrate:

   ```bash
   bench --site your-site migrate
   ```

On Frappe Cloud: add Sigzen MSME to your bench from the Marketplace, then install it on your site.

## Setup

1. MSME Settings: enter with/without contract payable days and interest %, and choose where MSME details are kept (Supplier or Address).

2. Supplier > MSME Details tab: add the supplier's MSME registration rows. When the MSME type changes, close the old row with an Effective To date and add a new row.

   Each row holds the Udyam number, MSME type and contract status for that period.

   If MSME details are kept on the Address instead, the same table appears under Address > License Details tab.

   On save, conflicting rows are blocked, for example the same Udyam number as Micro and Small for overlapping dates.

3. Run the MSME Non-Compliance report with Company and Fiscal Year.

## How the report works

- Due Date = invoice date + payable days - 1 (counting the invoice date as day 1)
- Disallowed = paid after due date + still outstanding after due date
- Interest = Disallowed x Interest %
- Medium suppliers and invoices paid on time are not shown.

## Compatibility

Frappe / ERPNext v15 and v16. Requires ERPNext.

## Support

- https://github.com/Sigzen-Team/sigzen_msme/issues
- https://www.sigzen.com

## License

MIT
