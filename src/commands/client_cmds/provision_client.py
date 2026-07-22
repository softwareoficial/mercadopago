import uuid
from sqlalchemy.orm import Session
from src.commands.base import BaseCommand
from src.core.models.models import Client
from src.core.integrations.hub_service import PlatformIntegrationService
from typing import Any, Dict

class ProvisionClientCommand(BaseCommand):
    """
    Command to activate a client on specific platforms and sync their identity.
    """

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        client_id = kwargs.get("client_id")
        platforms = kwargs.get("platforms", []) # ['whatsapp', 'stock']

        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client {client_id} not found.")

        # Ensure client has a global_tenant_id
        if not client.global_tenant_id:
            client.global_tenant_id = f"tenant_{uuid.uuid4().hex[:8]}"
            db.commit()

        hub = PlatformIntegrationService()
        results = {}

        if 'whatsapp' in platforms:
            success = hub.provision_whatsapp_hub({"email": client.email, "global_tenant_id": client.global_tenant_id})
            client.has_whatsapp_hub = 1 if success else 0
            results['whatsapp'] = "success" if success else "failed"

        if 'stock' in platforms:
            success = hub.provision_stock_pro({"name": client.name, "global_tenant_id": client.global_tenant_id})
            client.has_stock_pro = 1 if success else 0
            results['stock'] = "success" if success else "failed"

        db.commit()
        return {"status": "provisioned", "details": results}
