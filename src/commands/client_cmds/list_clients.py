from sqlalchemy.orm import Session
from src.commands.base import BaseCommand
from src.core.models.models import Client, Payment
from typing import List, Any

class ListClientsCommand(BaseCommand):
    """
    Lists all registered clients in the system.
    """
    def execute(self, db: Session, **kwargs) -> List[Any]:
        clients = db.query(Client).all()
        return [{"id": c.id, "name": c.name, "email": c.email} for c in clients]
