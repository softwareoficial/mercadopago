import argparse
import requests
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de la API Master (Railway Internal o Public)
API_BASE = os.getenv("MASTER_API_URL", "http://localhost:5000")

def call_api(endpoint, method="POST", data=None, headers=None):
    url = f"{API_BASE}{endpoint}"
    default_headers = {"Content-Type": "application/json", "X-Admin-ID": "CLI_MASTER_ADMIN"}
    if headers:
        default_headers.update(headers)
    
    try:
        if method == "POST":
            r = requests.post(url, json=data, headers=default_headers)
        elif method == "GET":
            r = requests.get(url, headers=default_headers)
        else:
            r = requests.request(method, url, json=data, headers=default_headers)
        
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ Error calling API: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="🚀 Master Control Plane CLI - SuperAdmin Tools")
    subparsers = parser.add_subparsers(dest="command")

    # --- GRANT ---
    grant_parser = subparsers.add_parser("grant", help="Grant a feature to a tenant")
    grant_parser.add_argument("--tenant", required=True, help="Tenant ID")
    grant_parser.add_argument("--feature", required=True, help="Feature ID (e.g., whatsapp.bot_core)")
    grant_parser.add_argument("--days", type=int, help="Duration in days (optional)")

    # --- REVOKE ---
    revoke_parser = subparsers.add_parser("revoke", help="Revoke a feature from a tenant")
    revoke_parser.add_argument("--tenant", required=True, help="Tenant ID")
    revoke_parser.add_argument("--feature", required=True, help="Feature ID")

    # --- AUDIT ---
    audit_parser = subparsers.add_parser("audit", help="Audit active features for a tenant")
    audit_parser.add_argument("--tenant", required=True, help="Tenant ID")

    args = parser.parse_args()

    if args.command == "grant":
        data = {"tenant_id": args.tenant, "feature_id": args.feature, "duration_days": args.days}
        res = call_api("/api/master/license/grant", data=data)
        print(f"✅ {res}")
    elif args.command == "revoke":
        data = {"tenant_id": args.tenant, "feature_id": args.feature}
        res = call_api("/api/master/license/revoke", data=data)
        print(f"✅ {res}")
    elif args.command == "audit":
        res = call_api(f"/api/master/license/audit/{args.tenant}", method="GET")
        print(f"🔍 Audit Results for {args.tenant}:")
        print(json.dumps(res, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
