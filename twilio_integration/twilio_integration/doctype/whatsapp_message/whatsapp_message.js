// Copyright (c) 2021, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('WhatsApp Message', {
	refresh: function (frm) {
		if (frm.doc.reference_doctype && frm.doc.reference_name) {
			frm.add_custom_button(__(frm.doc.reference_name), () => {
				frappe.set_route("Form", frm.doc.reference_doctype, frm.doc.reference_name);
			});
		}

		if (frm.doc.status == "Not Sent" && frm.doc.sent_received == "Sent") {
			let button = frm.add_custom_button("Send Now", function () {
				frappe.call({
					method: "twilio_integration.twilio_integration.doctype.whatsapp_message.whatsapp_message.send_now",
					args: {
						message_name: frm.doc.name,
					},
					freeze: 1,
					btn: button,
					callback: () => {
						frm.reload_doc();
					},
				});
			});
		}

		if (frm.doc.id && frm.doc.sent_received == "Sent") {
			let button = frm.add_custom_button("Update Delivery Status", function () {
				frappe.call({
					method: "twilio_integration.twilio_integration.doctype.whatsapp_message.whatsapp_message.reconcile_status_now",
					args: {
						message_name: frm.doc.name,
					},
					freeze: 1,
					btn: button,
					callback: () => {
						frm.reload_doc();
					},
				});
			});
		}
	},
});
