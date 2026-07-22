from sqlalchemy.orm import Session
from src.commands.base import BaseCommand
from src.core.models.models import Payment
from src.core.license_manager import LicenseManager
from typing import Any

class UpdatePaymentStatusCommand(BaseCommand):
    """
    Updates the status of a specific payment.
    Simulates the result of a Mercado Pago webhook notification.
    When a payment is 'approved', it automatically grants the corresponding license.
    """
    def execute(self, db: Session, payment_id: int, status: str, **kwargs) -> Any:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError(f"Payment with ID {payment_id} not found.")
        
        if status not in ["pending", "approved", "rejected"]:
            raise ValueError(f"Invalid status: {status}. Must be pending, approved, or rejected.")
            
        payment.status = status
        db.commit()
        
        # --- AUTOMATIC LICENSE ACTIVATION ---
        if status == "approved":
            # The payment model should ideally have a 'feature_id' or 'plan_id'. 
            # For now, we assume a payment for 'approved' status grants 'stock_pro_core'.
            # We use the client_id from the payment record as the tenant_id.
            lm = LicenseManager(db)
            feature_id = kwargs.get("feature_id", "stock_pro_core")
            lm.grant_feature(payment.client_id, feature_id, duration_days=365)
            
        return {"payment_id": payment.id, "new_status": payment.status, "license_granted": (status == "approved")}
