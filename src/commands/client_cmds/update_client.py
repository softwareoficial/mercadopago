from sqlalchemy.orm import Session
from src.commands.base import BaseCommand
from src.core.models.models import Client
from typing import Any, Dict

class UpdateClientCommand(BaseCommand):
    """
    Updates the details and credentials of an existing client.
    """
    def execute(self, db: Session, client_id: int, **data) -> Any:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client with ID {client_id} not found.")

        # Update only the fields provided in the request
        if "name" in data:
            client.name = data["name"]
        if "email" in data:
            client.email = data["email"]
        if "access_token" in data:
            client.access_token = data["access_token"]
        if "public_key" in data:
            client.public_key = data["public_key"]
        if "client_id" in data:
            client.client_id = data["client_id"]
        if "client_secret" in data:
            client.client_secret = data["client_secret"]
        if "webhook_secret" in data:
            client.webhook_secret = data["webhook_secret"]
        if "has_whatsapp_hub" in data:
            client.has_whatsapp_hub = data["has_whatsapp_hub"]
        if "has_stock_pro" in data:
            client.has_stock_pro = data["has_stock_pro"]
        if "account_status" in data:
            client.account_status = data["account_status"]

        db.commit()
        
        return {
            "id": client.id,
            "name": client.name,
            "status": "success"
        }
