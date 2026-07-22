import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sqlalchemy.orm import Session
from src.core.db import get_db, init_db, SessionLocal
from src.commands.registry import CommandRegistry

# Calculate the path to the web folder relative to this file
current_dir = os.path.dirname(os.path.abspath(__file__))
static_folder_path = os.path.join(current_dir, '..', 'web')

app = Flask(__name__, static_folder=static_folder_path)
CORS(app)

@app.route("/", methods=["GET"])
def serve_index():
    """Serves the Admin Panel HTML file."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/static/<path:path>")
def send_static(path):
    """Serves static assets (JS, CSS) from the web folder."""
    return send_from_directory(app.static_folder, path)

@app.route("/commands", methods=["GET"])
def list_commands():
    """Lists all available commands in the system."""
    return jsonify({"available_commands": CommandRegistry.list_commands()})

@app.route("/clients", methods=["GET"])
def get_clients():
    """Lists all clients, mapped to frontend expectations."""
    try:
        infra = InfraAPIClient()
        result = infra.execute("list-owners", {})
        
        # Mapeo: Infra devuelve 'owners', Frontend espera 'clients'
        owners = result.get("owners", [])
        mapped_clients = []
        for o in owners:
            # private_config está en el objeto root del owner
            sub = o.get("private_config", {}).get("subscription", {})
            mapped_clients.append({
                "id": o.get("cliente_id"),
                "name": o.get("cliente_nombre") or o.get("username"),
                "email": o.get("username"),
                "account_status": "active", # Placeholder por ahora
                "has_whatsapp_hub": False, # Placeholder
                "has_stock_pro": sub.get("plan") == "pro"
            })
            
        return jsonify({"status": "success", "clients": mapped_clients})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

@app.route("/clients", methods=["POST"])
def create_client():
    """Creates a new client tenant."""
    data = request.json
    db = SessionLocal()
    try:
        cmd = CommandRegistry.get_command("client:create")
        client = cmd.execute(db=db, **data)
        return jsonify({"status": "success", "client_id": client.id, "name": client.name}), 201
    except ValueError as e:
        return jsonify({"status": "error", "detail": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
    finally:
        db.close()

@app.route("/clients/<int:client_id>", methods=["PATCH"])
def update_client(client_id):
    """Updates a client's details and Mercado Pago credentials."""
    data = request.json
    db = SessionLocal()
    try:
        cmd = CommandRegistry.get_command("client:update")
        result = cmd.execute(db=db, client_id=client_id, **data)
        return jsonify({"status": "success", **result})
    except ValueError as e:
        return jsonify({"status": "error", "detail": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
    finally:
        db.close()

@app.route("/payments/all", methods=["GET"])
def list_all_payments():
    """Lists all payments across all clients."""
    db = SessionLocal()
    try:
        cmd = CommandRegistry.get_command("payment:all")
        payments = cmd.execute(db=db)
        return jsonify({"status": "success", "payments": payments})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
    finally:
        db.close()

@app.route("/payments/<int:payment_id>/status", methods=["PATCH"])
def update_payment_status(payment_id):
    """Updates the status of a specific payment."""
    data = request.json
    db = SessionLocal()
    try:
        cmd = CommandRegistry.get_command("payment:update_status")
        result = cmd.execute(db=db, payment_id=payment_id, status=data.get("status"))
        return jsonify({"status": "success", **result})
    except ValueError as e:
        return jsonify({"status": "error", "detail": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
    finally:
        db.close()

@app.route("/payments", methods=["POST"])
def create_payment():
    """Creates a payment preference for a client."""
    data = request.json
    db = SessionLocal()
    try:
        cmd = CommandRegistry.get_command("payment:create")
        result = cmd.execute(db=db, **data)
        return jsonify({"status": "success", **result}), 201
    except ValueError as e:
        return jsonify({"status": "error", "detail": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
    finally:
        db.close()

@app.route("/payments/<int:client_id>", methods=["GET"])
def list_payments(client_id):
    """Lists all payments for a specific client."""
    db = SessionLocal()
    try:
        cmd = CommandRegistry.get_command("payment:list")
        payments = cmd.execute(db=db, client_id=client_id)
        return jsonify({"status": "success", "payments": payments})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
    finally:
        db.close()

@app.route("/provision", methods=["POST"])
def provision_client():
    """Provisions a client across selected platforms."""
    data = request.json
    db = SessionLocal()
    try:
        cmd = CommandRegistry.get_command("client:provision")
        result = cmd.execute(db=db, **data)
        return jsonify({"status": "success", **result})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
    finally:
        db.close()

from src.core.infra_api_client import InfraAPIClient

@app.route("/subscriptions", methods=["GET"])
def list_subscriptions():
    """Endpoint para la sección 'Suscripciones': Lista todos los dueños y su plan actual."""
    try:
        infra = InfraAPIClient()
        result = infra.execute("list-owners", {})
        
        owners = result.get("owners", [])
        mapped_subs = []
        for o in owners:
            sub = o.get("private_config", {}).get("subscription", {})
            mapped_subs.append({
                "id": o.get("cliente_id"),
                "username": o.get("username"),
                "cliente_nombre": o.get("cliente_nombre"),
                "plan": sub.get("plan", "free"),
                "expiry_date": sub.get("plan_expiry_date"),
                "status": "active" if sub.get("plan") != "free" else "inactive"
            })
            
        return jsonify({"status": "success", "subscriptions": mapped_subs})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

@app.route("/api/admin/subscriptions/update", methods=["POST"])
def update_subscription_plan():
    """Actualiza el plan de un cliente manualmente desde la interfaz administrativa."""
    data = request.json
    try:
        infra = InfraAPIClient()
        # Llamamos al comando 'client-update-plan' que definimos en infra/client.js
        result = infra.execute("client-update-plan", {
            "clienteId": data.get("clienteId"),
            "plan": data.get("plan"),
            "expiryDate": data.get("expiryDate")
        })
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

@app.route("/subscriptions", methods=["POST"])
def create_subscription():
    """Creates a new subscription for a client."""
    data = request.json
    db = SessionLocal()
    try:
        cmd = CommandRegistry.get_command("subscription:create")
        result = cmd.execute(db=db, **data)
        return jsonify({"status": "success", **result}), 201
    except ValueError as e:
        return jsonify({"status": "error", "detail": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
    finally:
        db.close()

@app.route("/clients/<int:client_id>/status", methods=["PATCH"])
def update_client_status(client_id):
    """Updates the account status of a client."""
    data = request.json
    db = SessionLocal()
    try:
        cmd = CommandRegistry.get_command("client:update_status")
        result = cmd.execute(db=db, client_id=client_id, status=data.get("status"))
        return jsonify({"status": "success", **result})
    except ValueError as e:
        return jsonify({"status": "error", "detail": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
    finally:
        db.close()

# --- MASTER CONTROL PLANE API ---

@app.route("/api/master/license/grant", methods=["POST"])
def master_grant_license():
    """Grants a specific feature to a tenant. (SuperAdmin only)"""
    data = request.json
    db = SessionLocal()
    try:
        cmd = CommandRegistry.get_command("license:grant")
        # Pass admin_id from header or request
        admin_id = request.headers.get("X-Admin-ID", "MASTER_API")
        result = cmd.execute(db=db, 
                             tenant_id=data.get("tenant_id"), 
                             feature_id=data.get("feature_id"), 
                             duration_days=data.get("duration_days"), 
                             admin_id=admin_id)
        return jsonify({"status": "success", **result})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
    finally:
        db.close()

@app.route("/api/master/license/revoke", methods=["POST"])
def master_revoke_license():
    """Revokes a specific feature from a tenant. (SuperAdmin only)"""
    data = request.json
    db = SessionLocal()
    try:
        cmd = CommandRegistry.get_command("license:revoke")
        admin_id = request.headers.get("X-Admin-ID", "MASTER_API")
        result = cmd.execute(db=db, 
                             tenant_id=data.get("tenant_id"), 
                             feature_id=data.get("feature_id"), 
                             admin_id=admin_id)
        return jsonify({"status": "success", **result})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
    finally:
        db.close()

@app.route("/api/master/license/audit/<string:tenant_id>", methods=["GET"])
def master_audit_license(tenant_id):
    """Returns all active features for a specific tenant. (SuperAdmin only)"""
    db = SessionLocal()
    try:
        cmd = CommandRegistry.get_command("license:audit")
        result = cmd.execute(db=db, tenant_id=tenant_id)
        return jsonify({"status": "success", **result})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
    finally:
        db.close()


