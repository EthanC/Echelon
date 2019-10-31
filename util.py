import json
import logging

import requests

log = logging.getLogger(__name__)


class Utility:
    """Class containing utilitarian functions intended to reduce duplicate and messy code."""

    def ReadFile(self, filename: str, extension: str):
        """Read and return the contents of the specified file."""

        try:
            with open(f"{filename}.{extension}", "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            log.error(f"Failed to read {filename}.{extension}, {e}")

    def Webhook(self, url: str, data: dict):
        """ToDo"""

        headers = {"content-type": "application/json"}
        data = json.dumps(data)

        req = requests.post(url, headers=headers, data=data)

        # HTTP 204 (No Content)
        if req.status_code == 204:
            return True
        else:
            log.error(f"Failed to POST Webhook (HTTP {req.status_code})")

            return False
