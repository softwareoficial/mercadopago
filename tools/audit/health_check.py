import requests
import logging
from src.core.db import SessionLocal
from src.core.models.models import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AuditTool")

def check_platform_connectivity():
    """
    Checks if the Hub can communicate with the other deployed platforms.
    """
    targets = {
        "WhatsApp Hub": "http://localhost:5002/api",
        "Stock Pro": "http://localhost:8888"
    }
    
    print("
🔍 Starting Platform Connectivity Audit...
")
    for name, url in targets.items():
        try:
            res = requests.get(url, timeout=5)
            status = "✅ ONLINE" if res.status_code == 200 else f"⚠️ UNKNOWN ({res.status_code})"
            print(f"{name}: {status} - {url}")
        except Exception as e:
            print(f"{name}: ❌ OFFLINE - {str(e)}")

def audit_clients():
    """
    Checks for clients that are created but not yet provisioned.
    """
    db = SessionLocal()
    clients = db.query(Client).all()
    
    print("
👥 Auditing Client Provisioning Status...
")
    for c in clients:
        wa = "OK" if c.has_whatsapp_hub else "MISSING"
        stock = "OK" if c.has_stock_pro else "MISSING"
        print(f"Client: {c.name} | WA: {wa} | Stock: {stock}")
    db.close()

if __name__ == "__main__":
    check_platform_connectivity()
    audit_clients()
