from sqlalchemy.orm import Session
from src.commands.base import BaseCommand
from src.core.models.models import Payment
from typing import List, Any

class ListPaymentsCommand(BaseCommand):
    """
    Lists all payments for a specific client.
    """
    def execute(self, db: Session, **kwargs) -> List[Any]:
        client_id = kwargs.get("client_id")
        if not client_id:
            raise ValueError("client_id is mandatory.")
            
        payments = db.query(Payment).filter(Payment.client_id == client_id).all()
        return [
            {
                "id": p.id, 
                "preference_id": p.preference_id, 
                "init_point": p.init_point,
                "amount": p.amount, 
                "status": p.status, 
                "created_at": p.created_at
            } for p in payments
        ]
