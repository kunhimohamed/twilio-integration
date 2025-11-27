import frappe
from frappe import _
from twilio_integration.twilio_integration.doctype.whatsapp_message.whatsapp_message import WhatsAppMessage, \
	are_whatsapp_messages_muted
from frappe.core.doctype.notification_count.notification_count import set_notification_last_scheduled
from frappe.email.doctype.notification.notification import (
	Notification,
	json,
	get_reference_doctype,
	get_reference_name,
)


class NotificationTwilio(Notification):
	def validate(self):
		super().validate()
		self.validate_twilio_settings()
		self.validate_whatsapp_template()

	def validate_twilio_settings(self):
		if self.enabled and self.channel == "WhatsApp":
			whatsapp_settings = frappe.get_single("WhatsApp Settings")
			if not whatsapp_settings.whatsapp_no:
				frappe.throw(_("WhatsApp Number is required in WhatsApp Settings"))
			if whatsapp_settings.whatsapp_provider == "Twilio":
				twilio_settings = frappe.get_single("Twilio Settings")
				if not twilio_settings.enabled:
					frappe.throw(_("Twilio Settings must be enabled to send WhatsApp notifications"))
			elif whatsapp_settings.whatsapp_provider == "Freshchat":
				freshchat_settings = frappe.get_single("Freshchat Settings")
				if not freshchat_settings.enabled:
					frappe.throw(_("Freshchat Settings must be enabled to send WhatsApp notifications"))
			else:
				frappe.throw(_("Please configure WhatsApp Provider"))

			if whatsapp_settings.whatsapp_provider == "Freshchat" and not self.use_whatsapp_template:
				frappe.throw(_("Freshchat does not allow non-template messages. Please select WhatsApp Message Template instead"))

	def validate_whatsapp_template(self):
		if self.use_whatsapp_template:
			if not self.whatsapp_message_template:
				frappe.throw(_("Please select WhatsApp Template Message"))
		else:
			self.whatsapp_message_template = None

	def send(self, doc, context=None):
		if not context:
			context = {}

		context.update({"doc": doc, "alert": self, "comments": None})

		if doc.get("_comments"):
			context["comments"] = json.loads(doc.get("_comments"))

		if self.is_standard:
			self.load_standard_properties(context)

		try:
			if self.channel == 'WhatsApp':
				self.send_whatsapp_msg(doc, context)
		except Exception:
			frappe.log_error(
				message=frappe.get_traceback(),
				title=_("Failed to send WhatsApp Notification: {0}").format(self.name),
				reference_doctype=get_reference_doctype(doc),
				reference_name=get_reference_name(doc),
			)

		super().send(doc, context=context)

	def send_whatsapp_msg(self, doc, context):
		if are_whatsapp_messages_muted():
			return

		receiver_list = self.get_receiver_list(doc, context)
		receiver_list = format_numbers_for_whatsapp(receiver_list)
		if not receiver_list:
			return

		ref_doctype = get_reference_doctype(doc)
		ref_name = get_reference_name(doc)

		notification_type = self.get_notification_type()

		if notification_type:
			set_notification_last_scheduled(
				ref_doctype,
				ref_name,
				notification_type,
				"WhatsApp",
				child_doctype=context.get("child_doctype"),
				child_name=context.get("child_name"),
			)

		whatsapp_message_template = None
		content_variables = None

		if self.use_whatsapp_template and self.whatsapp_message_template:
			template = frappe.get_cached_doc("WhatsApp Message Template", self.whatsapp_message_template)
			whatsapp_message_template = self.whatsapp_message_template

			content_variables = template.get_content_variables(context)
			message = template.get_rendered_body(context, content_variables=content_variables)
		else:
			message = frappe.render_template(self.message, context)

		self.flags.message = message

		timeline_doctype, timeline_name = self.get_timeline_doctype_and_name(doc)

		attachments = self.get_attachment(doc)

		WhatsAppMessage.send_whatsapp_message(
			receiver_list=receiver_list,
			message=message,
			notification_type=notification_type,
			reference_doctype=ref_doctype,
			reference_name=ref_name,
			child_doctype=context.get("child_doctype"),
			child_name=context.get("child_name"),
			party_doctype=timeline_doctype,
			party=timeline_name,
			whatsapp_message_template=whatsapp_message_template,
			whatsapp_reply_handler=self.whatsapp_reply_handler,
			content_variables=content_variables or None,
			automated=True,
			attachment=attachments[0] if attachments else None,
			now=False,
		)


def format_numbers_for_whatsapp(receiver_list):
	"""Format phone numbers to international format"""
	from frappe.regional.regional import local_to_international_mobile_no

	formatted_list = []
	for number in receiver_list:
		if not number:
			continue

		formatted_number = local_to_international_mobile_no(number)
		formatted_list.append(formatted_number)

	return formatted_list
