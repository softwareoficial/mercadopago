import requests
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MPService")

class MercadoPagoError(Exception):
    """Custom exception for Mercado Pago API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

class MPService:
    """
    A wrapper service for the Mercado Pago API.
    This service is stateless; it requires credentials to be passed in for each call.
    """
    
    BASE_URL = "https://api.mercadopago.com"

    def __init__(self):
        pass

    def _request(self, method: str, endpoint: str, access_token: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generic request helper to handle Mercado Pago API communication.
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.request(method, url, headers=headers, json=data, timeout=10)
            if response.status_code >= 400:
                logger.error(f"MP API Error: {response.status_code} - {response.text}")
                raise MercadoPagoError(
                    f"Mercado Pago API returned error: {response.text}",
                    status_code=response.status_code,
                    response_body=response.json() if response.content else None
                )
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.exception(f"Network error connecting to Mercado Pago: {e}")
            raise MercadoPagoError(f"Failed to connect to Mercado Pago API: {str(e)}")

    def create_preference(self, access_token: str, amount: float, title: str, description: str, currency: str = "ARS", external_reference: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a payment preference (payment link).
        
        Args:
            access_token: Client's MP access token.
            amount: Price of the product.
            title: Product title.
            description: Product description.
            currency: Currency ID (default ARS).
            external_reference: Optional ID to track the payment.
            
        Returns:
            The preference JSON containing 'init_point' and 'id'.
        """
        endpoint = "/checkout/preferences"
        body = {
            "items": [
                {
                    "title": title,
                    "quantity": 1,
                    "unit_price": amount,
                    "currency_id": currency
                }
            ],
            "external_reference": external_reference
        }
        return self._request("POST", endpoint, access_token, body)

    def get_payment_details(self, access_token: str, payment_id: str) -> Dict[str, Any]:
        """
        Retrieves the status and details of a specific payment.
        """
        endpoint = f"/v1/payments/{payment_id}"
        return self._request("GET", endpoint, access_token)
