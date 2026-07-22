from typing import List, Dict, Any
from sqlalchemy.orm import Session
from src.commands.base import BaseCommand
from src.core.models.models import Subscription

class ListSubscriptionsCommand(BaseCommand):
    """
    Retrieves all subscriptions associated with a specific client.
    """
    def execute(self, db: Session, client_id: int) -> List[Dict[str, Any]]:
        subscriptions = db.query(Subscription).filter(Subscription.client_id == client_id).all()
        
        return [
            {
                "id": s.id,
                "subscription_id": s.subscription_id,
                "plan_id": s.plan_id,
                "amount": s.amount,
                "frequency": s.frequency,
                "status": s.status,
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in subscriptions
        ]
