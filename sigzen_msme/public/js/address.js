// Show the "License Details" tab only when MSME Settings > MSME Detail Source = Address.
frappe.ui.form.on("Address", {
	refresh(frm) {
		frappe.db.get_single_value("MSME Settings", "msme_detail_source").then((source) => {
			const show = (source || "Supplier") === "Address";
			frm.toggle_display("custom_license_details_tab", show);
			frm.toggle_display("custom_msme_details", show);
		});
	},
});
