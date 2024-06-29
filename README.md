## Sigzen Msme

Sigzen Msme

#### License

MIT

**Sigzen MSME**

**Introduction to MSME in India**

Micro, Small, and Medium Enterprises (MSMEs) play a crucial role in the Indian economy, contributing significantly to employment generation, innovation, and economic development. MSMEs are categorized based on their investment in plant and machinery or equipment and annual turnover. The Government of India provides various schemes and incentives to support the growth and sustainability of MSMEs.

**Overview of Sigzen MSME App**

The Sigzen MSME app is designed to enhance ERPNext by adding functionalities specific to MSME requirements. This documentation provides a detailed guide on installation, configuration, and usage of the app, ensuring compliance with MSME regulations in India.

**Installation**

**Prerequisites**

    Frappe Framework installed

    Basic knowledge of Frappe and ERPNext
    
**Steps**

**Clone the repository:**

    git clone https://github.com/your-repo/sigzen_msme.git

**Navigate to the app directory:**

    cd sigzen_msme

**Install the app:**

    bench get-app sigzen_msme /path/to/sigzen_msme
    bench install-app sigzen_msme

**Apply patches and migrate:**

    bench migrate


**Doctype**

**1. MSME Settings**

The "MSME Settings" DocType allows users to configure various settings related to Micro, Small, and Medium Enterprises (MSME) contracts. This includes specifying the number of payable days with a contract and without a contract.

**Fields:**

**With Contract Payable Days:** Enter the number of days within which payment should be made when a contract exists.

**Without Contract Payable Days:** Enter the number of days within which payment should be made when no contract exists.

<img width="960" alt="MSME Settings" src="https://github.com/Sigzen-Team/sigzen_msme/assets/146057623/e4f5536d-b9b6-49bc-9cb0-c7248a3d99dc">


**2. Supplier**

In the Sigzen MSME app, custom fields have been added to the "Supplier" Doctype to capture MSME-specific details. These fields help track whether a supplier is registered as an MSME, their registration number, the type of MSME, and the contract status.

**Custom Fields:**

**MSME Registered:** Indicates whether the supplier is registered as an MSME. Select "Yes" if registered, otherwise select "No".

**MSME Registration No:** Captures the MSME registration number of the supplier. This field is required if the "MSME Registered" field is set to "Yes".

**MSME Type:** Specifies the type of MSME the supplier is registered as. Options include "Micro," "Small," or "Medium". This field is required if the "MSME Registered" field is set to "Yes".

**MSME Contract Done:** Indicates whether an MSME contract has been done with the supplier. This field is required if the "MSME Registered" field is set to "Yes".

<img width="960" alt="Supplier" src="https://github.com/Sigzen-Team/sigzen_msme/assets/146057623/7275bc93-4ec3-489b-8ffd-032bbb003695">


**3. Purchase Invoice**

The "Purchase Invoice" Doctype is used to record invoices received from suppliers.

**Creating a Purchase Invoice:**

Go to the "Purchase Invoice" section.

Click on "New" to create a new purchase invoice.

**Fill in the required details:**

**Supplier:** Select the supplier from whom the invoice is received.

**Posting Date:** Enter the date when the invoice is recorded in the system.

**Bill Date:** Enter the date of the supplier's invoice.

**Invoice Amount:** Enter the total amount of the invoice.

Save and submit the invoice.

**4. Payment Entry**

The "Payment Entry" Doctype is used to record payments made to suppliers.

**Creating a Payment Entry:**

Go to the "Payment Entry" section.

Click on "New" to create a new payment entry.

**Fill in the required details:**

**Payment Type:** Select "Pay" for payments to suppliers.

**Party Type:** Select "Supplier".

**Party:** Select the supplier to whom the payment is made.

**Payment Amount:** Enter the amount paid.

**Reference No:** Enter the reference number for the payment (e.g., bank transaction ID).

**Posting Date:** Enter the date the payment is recorded in the system.

Save and submit the payment entry.


**Report**

**MSME Non-Compliance**

**Overview**

The MSME Non-Compliance report in the Sigzen MSME project provides a detailed overview of supplier invoices, payment statuses, and compliance with MSME regulations. This report is a vital tool for ensuring timely payments, maintaining financial health, and adhering to MSME regulations.

**Setting Filters**

**Before running the MSME report, you need to set the appropriate filters:**

**From Date:** Select the start date for the report.

**To Date:** Select the end date for the report.

**Supplier:** (Optional) Select a specific supplier to filter the report.

**Supplier Group:** (Optional) Select a specific supplier group to filter the report.

**MSME Type:** (Optional) Select the MSME type (Micro, Small, Medium) to filter the report.

**Contract Done:** (Optional) Select whether to filter suppliers with MSME contracts done.


<img width="960" alt="Report0" src="https://github.com/Sigzen-Team/sigzen_msme/assets/146057623/fc89beae-480f-4ac1-9357-2924130f0b6c">


<img width="960" alt="Report1" src="https://github.com/Sigzen-Team/sigzen_msme/assets/146057623/f9d5577c-3c93-4aff-bd24-85c7c97d5852">


**Report Columns**

**The report includes the following columns:**

**Purchase ID:** The ID of the purchase invoice.

**Supplier:** The name of the supplier.

**Supplier No:** The supplier number.

**MSME Contract Done:** Indicates whether an MSME contract has been done.

**Posting Date:** The date the invoice was posted (if applicable).

**Supplier Invoice Date:** The date of the supplier's invoice (if applicable).

**Due Date:** The due date for payment.

**Invoice Amount:** The total amount of the invoice.

**Current Outstanding:** The outstanding amount on the invoice.

**Paid Amt Before Due Dt:** The amount paid before the due date.

**Paid Amt After Due Dt:** The amount paid after the due date.

**Disallowed Amount:** The amount disallowed (if applicable).



