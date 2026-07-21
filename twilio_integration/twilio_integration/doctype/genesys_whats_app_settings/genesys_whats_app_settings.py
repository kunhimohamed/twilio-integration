# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document


class GenesysWhatsAppSettings(Document):
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
