app_name = "twilio_integration"
app_title = "Twilio Integration"
app_publisher = "Frappe"
app_description = "Custom Frappe Application for Twilio Integration"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "developers@frappe.io"
app_license = "MIT"

# app_include_css = "/assets/twilio_integration/css/twilio_call_handler.css"
# app_include_js = "/assets/twilio_integration/js/twilio_call_handler.js"

boot_session = "twilio_integration.boot.boot_session"

override_whitelisted_methods = {
	"twilio.incoming_whatsapp_message_handler": "twilio_integration.twilio_integration.api.incoming_whatsapp_message_handler",
	"twilio.whatsapp_media": "twilio_integration.twilio_integration.api.download_whatsapp_media",
	"twilio.whatsapp_message_status_callback": "twilio_integration.twilio_integration.api.whatsapp_message_status_callback",
	"whatsapp.secure_whatsapp_media": "twilio_integration.twilio_integration.doctype.whatsapp_message.whatsapp_message.secure_whatsapp_media",
	"whatsapp.secure_whatsapp_media.pdf": "twilio_integration.twilio_integration.doctype.whatsapp_message.whatsapp_message.secure_whatsapp_media",
	# "twilio.webhook_sink_handler": "twilio_integration.twilio_integration.api.whatsapp_message_status_callback",
}

website_redirects = [
	{
		"source": r"/twilio-whatsapp-media/(.*)",
		"target": r"/api/method/twilio.whatsapp_media?id=\1",
	}
]

override_doctype_class = {
	"Notification": "twilio_integration.overrides.notification_hooks.NotificationTwilio",
	"Communication": "twilio_integration.overrides.communication_hooks.CommunicationTwilio",
}

doctype_js = {
	"Notification": "overrides/notification_hooks.js",
	# "Voice Call Settings": "public/js/voice_call_settings.js"
}

fixtures = [
	{
		"dt": "Custom Field",
		"filters": {
			"name": ["in", [
				"Notification-sec_whatsapp_template",
				"Notification-whatsapp_message_template",
				"Notification-use_whatsapp_template",
				"Notification-custom_column_break_nckpb",
				"Notification-whatsapp_reply_handler",
			]]
		}
	},
	{
		"dt": "Property Setter",
		"filters": {
			"name": ["in", [
				"Notification-channel-options",
				"Communication Medium-communication_medium_type-options",
			]]
		}
	}
]

scheduler_events = {
	"all": [
		"twilio_integration.twilio_integration.doctype.whatsapp_message.whatsapp_message.flush_outgoing_message_queue",
	],
	"hourly_long": [
		"twilio_integration.twilio_integration.doctype.whatsapp_message.whatsapp_message.update_messages_pending_status_reconciliation",
		"twilio_integration.twilio_integration.doctype.whatsapp_message.whatsapp_message.flush_incoming_media_queue",
	],
	"daily": [
		"twilio_integration.twilio_integration.doctype.whatsapp_message.whatsapp_message.expire_whatsapp_message_queue",
	],
}

page_renderer = "twilio_integration.twilio_integration.doctype.whatsapp_message.whatsapp_message.WhatsAppMediaRenderer"
