// Show the "MSME Details" tab only when MSME Settings > MSME Detail Source = Supplier.
frappe.ui.form.on("Supplier", {
	refresh(frm) {
		frappe.db.get_single_value("MSME Settings", "msme_detail_source").then((source) => {
			const show = (source || "Supplier") === "Supplier";
			frm.toggle_display("custom_msme_details_tab", show);
			frm.toggle_display("custom_msme_details", show);
		});
	},
});
