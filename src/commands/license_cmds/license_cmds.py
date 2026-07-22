from src.commands.base import BaseCommand
from typing import Dict, Any

class GrantLicenseCommand(BaseCommand):
    """
    Comando para otorgar una funcionalidad a un tenant.
    """
    def execute(self, db, tenant_id: str, feature_id: str, duration_days: int = None, admin_id: str = "SYSTEM") -> Dict[str, Any]:
        from src.core.license_manager import LicenseManager
        lm = LicenseManager(db)
        return lm.grant_feature(tenant_id, feature_id, duration_days, admin_id)

class RevokeLicenseCommand(BaseCommand):
    """
    Comando para revocar una funcionalidad a un tenant.
    """
    def execute(self, db, tenant_id: str, feature_id: str, admin_id: str = "SYSTEM") -> Dict[str, Any]:
        from src.core.license_manager import LicenseManager
        lm = LicenseManager(db)
        return lm.revoke_feature(tenant_id, feature_id, admin_id)

class AuditLicenseCommand(BaseCommand):
    """
    Comando para auditar todas las licencias de un tenant.
    """
    def execute(self, db, tenant_id: str) -> Dict[str, Any]:
        from src.core.license_manager import LicenseManager
        lm = LicenseManager(db)
        features = lm.audit_tenant(tenant_id)
        return {"status": "success", "data": features}
