from sqlalchemy.orm import Session
from src.commands.base import BaseCommand
from src.core.models.models import Client

class UpdateClientStatusCommand(BaseCommand):
    """
    Updates the account status of a client (e.g., active, suspended).
    """
    def execute(self, db: Session, client_id: int, status: str) -> dict:
        valid_statuses = ["active", "suspended", "pending"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
            
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client with ID {client_id} not found.")
            
        client.account_status = status
        db.commit()
        db.refresh(client)
        
        return {"status": "success", "client_id": client.id, "new_status": client.account_status}
