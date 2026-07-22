import requests
import os

class InfraAPIClient:
    """
    Cliente para comunicarse con el servicio 'infra' (infrastructure-engine).
    Centraliza las llamadas al API en lugar de acceder a la DB directamente.
    """
    def __init__(self):
        # URL del servicio 'infra' desplegado
        self.base_url = os.getenv("INFRA_API_URL", "http://infra-service:3001")
        # Token para autenticar las peticiones administrativas
        self.token = os.getenv("ADMIN_SECRET_TOKEN")

    def execute(self, cmd, payload):
        """
        Ejecuta un comando en el servicio 'infra' mediante POST /execute.
        """
        url = f"{self.base_url}/execute"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        body = {"command": cmd, "payload": payload, "token": self.token}
        
        try:
            response = requests.post(url, json=body, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Manejo de errores de red o API
            print(f"Error conectando con Infra API: {e}")
            raise Exception(f"InfraAPI Error: {str(e)}")
