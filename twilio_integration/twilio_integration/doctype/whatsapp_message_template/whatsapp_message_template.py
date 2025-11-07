# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cstr
from frappe import _
from twilio.base.exceptions import TwilioRestException


class WhatsAppMessageTemplate(Document):
	def validate(self):
		self.validate_button_variable()

	def validate_button_variable(self):
		if self.button_variable and self.button_variable not in [d.variable for d in self.parameters]:
			frappe.throw(_("Button variable {0} must be defined in the parameters table").format(
				frappe.bold(self.button_variable)
			))

	def get_content_variables(self, context):
		"""
		Returns a dictionary of variable:value pairs using the parameters child table.
		Each `value` is rendered using Jinja with the provided context.
		"""
		content_variables = frappe._dict()
		for param in self.parameters:
			if param.variable:
				value = cstr(param.value)
				if "{" in value:
					content_variables[param.variable] = frappe.render_template(value, context)
				else:
					content_variables[param.variable] = cstr(value)

		return content_variables

	def get_rendered_body(self, context, content_variables=None):
		"""
		Renders the `template_body` field using the context derived from parameters.
		"""
		if content_variables is None:
			content_variables = self.get_content_variables(context)

		return frappe.render_template(self.template_body, content_variables)


@frappe.whitelist()
def sync_twilio_template(template_sid):
	from ...twilio_handler import Twilio

	twilio = Twilio.connect()

	out = frappe._dict({
		"body": "",
		"variables": {},
	})

	try:
		content = twilio.get_whatsapp_template(template_sid)
		if not content:
			frappe.throw(_("Unable to fetch template from Twilio"))

		if content.types.get("twilio/text"):
			out.body = content.types.get("twilio/text", {}).get("body", "")
		else:
			for type, obj in content.types.items():
				out.body = obj.get("body", "")
				if out.body:
					break

		if content.variables:
			out.variables = content.variables

	except TwilioRestException as e:
		frappe.throw(_("Error fetching template from Twilio: {0}").format(e))

	return out
