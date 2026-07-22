from sqlalchemy.orm import Session
from src.commands.base import BaseCommand
from src.core.models.models import Client, Payment
from src.core.services.mp_service import MPService
from typing import Any, Dict

class CreatePaymentCommand(BaseCommand):
    """
    Command to create a payment preference for a specific client.
    """

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        """
        Creates a Mercado Pago preference and records it in the database.
        
        Expected kwargs:
            client_id: ID of the client owning the payment.
            amount: Amount to charge.
            title: Product title.
            description: Product description.
            currency: Currency (default ARS).
        """
        client_id = kwargs.get("client_id")
        amount = kwargs.get("amount")
        title = kwargs.get("title")
        description = kwargs.get("description", "")
        currency = kwargs.get("currency", "ARS")

        if not client_id or not amount or not title:
            raise ValueError("Missing required fields: client_id, amount, and title are mandatory.")

        # 1. Fetch client credentials
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client with ID {client_id} not found.")

        # 2. Call MP Service
        mp_service = MPService()
        mp_response = mp_service.create_preference(
            access_token=client.access_token,
            amount=amount,
            title=title,
            description=description,
            currency=currency
        )

        # 3. Record in Database
        payment = Payment(
            client_id=client_id,
            preference_id=mp_response.get("id"),
            init_point=mp_response.get("init_point"),
            amount=amount,
            currency=currency,
            description=description,
            status="pending"
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return {
            "payment_id": payment.id,
            "preference_id": payment.preference_id,
            "init_point": payment.init_point,
            "status": payment.status
        }
