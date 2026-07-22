# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.model.document import Document
from frappe.utils import validate_json_string


class GenesysWhatsAppSettings(Document):

	def validate(self):
		self.validate_body_parameters()

	def validate_body_parameters(self):
		for each_genesys_whatsapp_details in self.genesys_whatsapp_details:
			if each_genesys_whatsapp_details.reference_doctype and each_genesys_whatsapp_details.body_parameters:
				validate_json_string(
					each_genesys_whatsapp_details.body_parameters, each_genesys_whatsapp_details.idx, "Filters"
				)
				fields_dict = json.loads(each_genesys_whatsapp_details.body_parameters)
				for each_fields_dict in fields_dict:
					if frappe.get_meta(
						each_genesys_whatsapp_details.reference_doctype
					).has_field(each_fields_dict.get("field")):
						continue
					else:
						frappe.throw(
							f"the filter {frappe.bold(each_fields_dict.get('field'))} not available in the {frappe.bold(each_genesys_whatsapp_details.reference_doctype)}",
							title="Invalid Filter",
						)

	def get_access_token(self):
		CACHE_KEY = self.genesys_oauth_cache_key
		cached = frappe.cache().get_value(CACHE_KEY)
		if cached:
			return cached

		client_secret = self.get_password("client_secret")

		resp = requests.post(
			self.token_url,
			data={"grant_type": self.grant_type},
			auth=(self.client_id, client_secret),  # Basic Auth
			timeout=10,
		)

		resp.raise_for_status()
		token_data = resp.json()

		access_token = token_data["access_token"]
		expires_in = token_data.get("expires_in", 3600)

		# cache with a small buffer so we refresh before actual expiry
		frappe.cache().set_value(
			CACHE_KEY, access_token, expires_in_sec=expires_in - 1500
		)

		return access_token
