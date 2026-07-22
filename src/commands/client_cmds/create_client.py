from sqlalchemy.orm import Session
from src.commands.base import BaseCommand
from src.core.models.models import Client
from typing import Any

class CreateClientCommand(BaseCommand):
    """
    Command to create a new client tenant in the system.
    """

    def execute(self, db: Session, **kwargs) -> Client:
        """
        Creates a client in the database.
        
        Expected kwargs:
            name: Client's name.
            email: Client's email.
            access_token: Mercado Pago Access Token.
            public_key: Mercado Pago Public Key.
            client_id: MP Client ID.
            client_secret: MP Client Secret.
            webhook_secret: MP Webhook Secret.
        """
        name = kwargs.get("name")
        email = kwargs.get("email")
        access_token = kwargs.get("access_token")

        if not all([name, email, access_token]):
            raise ValueError("Missing required fields: name, email, and access_token are mandatory.")

        new_client = Client(
            name=name,
            email=email,
            access_token=access_token,
            public_key=kwargs.get("public_key"),
            client_id=kwargs.get("client_id"),
            client_secret=kwargs.get("client_secret"),
            webhook_secret=kwargs.get("webhook_secret")
        )
        
        db.add(new_client)
        db.commit()
        db.refresh(new_client)
        return new_client
