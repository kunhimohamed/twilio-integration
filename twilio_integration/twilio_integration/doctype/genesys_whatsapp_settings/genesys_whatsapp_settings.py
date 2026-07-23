# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint
from frappe.model.document import Document
from urllib.parse import urljoin
import requests

CACHE_KEY = "genesys_access_token"


class GenesysWhatsAppSettings(Document):
	def get_access_token(self):
		access_token = frappe.cache().get_value(CACHE_KEY)
		if access_token:
			return access_token

		url = urljoin(self.login_base_url, "/oauth/token")
		client_secret = self.get_password("client_secret")

		response = requests.post(
			url,
			data={"grant_type": "client_credentials"},
			auth=(self.client_id, client_secret),  # Basic Auth
			timeout=10,
		)

		response.raise_for_status()
		token_data = response.json()

		access_token = token_data.get("access_token")
		expires_in = cint(token_data.get("expires_in", 3600))
		expires_in = max(expires_in - 600, 0)

		# cache with a small buffer so we refresh before actual expiry
		if access_token and expires_in:
			frappe.cache().set_value(CACHE_KEY, access_token, expires_in_sec=expires_in)

		return access_token
