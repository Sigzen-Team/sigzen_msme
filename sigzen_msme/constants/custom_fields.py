b= {
    "Supplier": [
        {
            "fieldname": "custom_msme_detail_column_break",
            "fieldtype": "Section Break",
            "insert_after": "image",
            "label": "",
            "is_system_generated": 0
        },
        {
            "fieldname": "custom_msme_details",
            "fieldtype": "Table",
            "options" :  "MSME Details",
            "insert_after": "custom_msme_detail_column_break",
            "label": "MSME Details",
            "is_system_generated": 0
        }
    ],
    "Address": [
        {
            "fieldname": "custom_msme_details_sections",
            "fieldtype": "Section Break",
            "insert_after": "custom_iso_remark",
            "label": "MSME Details",
            "collapsible": 1,
            "is_system_generated": 0 
        },
        {
            "fieldname": "custom_is_msme",
            "fieldtype": "Check",
            "insert_after": "custom_msme_details_sections",
            "label": "Is MSME",
            "is_system_generated": 0
        }, 
        {
            "fieldname": "custom_msme_details",
            "fieldtype": "Table",
            "options" :  "MSME Details",
            "insert_after": "custom_is_msme",
            "depends_on": "eval:doc.custom_is_msme;",
            "label": "MSME Details",
            "is_system_generated": 0
        }
    ]
}