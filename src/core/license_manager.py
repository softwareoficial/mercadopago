import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from src.core.db import SessionLocal # Adjusting to use the SQLAlchemy session if needed, but we need Global DB access

# We need the GlobalDatabaseManager logic here as well because Payment Gateway 
# is the central hub for the Master Control Plane.
from src.core.models.models import Client

class LicenseManager:
    """
    Motor de Gestión de Licencias y Entitlements.
    Implementado en el Payment Gateway como núcleo del Master Control Plane.
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.logger = logging.getLogger("LicenseManager")

    def grant_feature(self, tenant_id: str, feature_id: str, duration_days: Optional[int] = None, admin_id: str = "SYSTEM") -> Dict[str, Any]:
        try:
            expires_at = None
            if duration_days:
                expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)
            
            query = '''
                INSERT INTO entitlements (tenant_id, feature_id, status, expires_at)
                VALUES (%s, %s, 'active', %s)
                ON CONFLICT (tenant_id, feature_id) 
                DO UPDATE SET 
                    status = 'active', 
                    expires_at = EXCLUDED.expires_at,
                    granted_at = CURRENT_TIMESTAMP
            '''
            self.db.execute(query, (tenant_id, feature_id, expires_at))
            self.log_action(admin_id, tenant_id, feature_id, "GRANT", "SUCCESS", f"Licencia otorgada por {duration_days if duration_days else 'perpetuo'} días.")
            return {"status": "success", "message": f"Feature {feature_id} otorgada a {tenant_id}."}
        except Exception as e:
            self.logger.error(f"Error granting feature {feature_id} to {tenant_id}: {e}")
            self.log_action("SYSTEM", tenant_id, feature_id, "GRANT", "ERROR", str(e))
            return {"status": "error", "message": str(e)}

    def revoke_feature(self, tenant_id: str, feature_id: str, admin_id: str = "SYSTEM") -> Dict[str, Any]:
        try:
            query = "UPDATE entitlements SET status = 'suspended' WHERE tenant_id = %s AND feature_id = %s"
            self.db.execute(query, (tenant_id, feature_id))
            self.log_action(admin_id, tenant_id, feature_id, "REVOKE", "SUCCESS", "Funcionalidad suspendida.")
            return {"status": "success", "message": f"Feature {feature_id} revocada para {tenant_id}."}
        except Exception as e:
            self.logger.error(f"Error revoking feature {feature_id} from {tenant_id}: {e}")
            self.log_action("SYSTEM", tenant_id, feature_id, "REVOKE", "ERROR", str(e))
            return {"status": "error", "message": str(e)}

    def verify_feature(self, tenant_id: str, feature_id: str) -> bool:
        try:
            query = 'SELECT status, expires_at FROM entitlements WHERE tenant_id = %s AND feature_id = %s'
            res = self.db.fetch_one(query, (tenant_id, feature_id))
            if not res or res['status'] != 'active':
                return False
            if res['expires_at'] and res['expires_at'] < datetime.now(timezone.utc):
                self.revoke_feature(tenant_id, feature_id, admin_id="SYSTEM_EXPIRATION")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error verifying feature {feature_id} for {tenant_id}: {e}")
            return False

    def audit_tenant(self, tenant_id: str) -> List[Dict[str, Any]]:
        try:
            query = "SELECT feature_id, status, expires_at FROM entitlements WHERE tenant_id = %s"
            results = self.db.fetch_all(query, (tenant_id,))
            return [dict(r) for r in results]
        except Exception as e:
            self.logger.error(f"Error auditing tenant {tenant_id}: {e}")
            return []

    def log_action(self, admin_id: str, tenant_id: str, feature_id: str, action: str, status: str, detail: str):
        try:
            log_detail = f"[{action}] FEATURE: {feature_id} | STATUS: {status} | DETAIL: {detail}"
            query = "INSERT INTO admin_logs (admin_id, action, details) VALUES (%s, %s, %s)"
            self.db.execute(query, (admin_id, "LICENSE_MGMT", log_detail))
        except Exception as e:
            self.logger.error(f"Error writing to admin_logs: {e}")
