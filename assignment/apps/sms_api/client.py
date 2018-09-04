from django.core.urlresolvers import reverse

from utils.api_client import APIClient, RequestType


class SMSAPIClient(APIClient):
    
    def send_inbound_request(self, auth, data, method=RequestType.POST):
        """Sends an inbound sms request."""

        url = "http://testserver" + reverse("inbound_sms")
        return self._send_request(url, method, auth, data)

    def send_outbound_request(self, auth, data, method=RequestType.POST):
        """Sends an outbound sms request."""

        url = reverse("outbound_sms")
        return self._send_request(url, method, auth, data)
