from sqlalchemy.orm import Session
from src.commands.base import BaseCommand
from src.core.models.models import Payment
from typing import List, Any

class ListAllPaymentsCommand(BaseCommand):
    """
    Lists all payments across all clients for administrative monitoring.
    """
    def execute(self, db: Session, **kwargs) -> List[Any]:
        # Fetch all payments joined with their client to get the client name
        payments = db.query(Payment).all()
        
        return [
            {
                "id": p.id, 
                "client_name": p.client.name,
                "client_id": p.client_id,
                "preference_id": p.preference_id, 
                "amount": p.amount, 
                "status": p.status, 
                "created_at": p.created_at
            } for p in payments
        ]
