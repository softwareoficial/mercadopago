# 🛠️ API Specification

## Base URL
`http://<service-url>/`

## Endpoints

### Clients
- `GET /clients`: Returns a list of all registered tenants.
- `POST /clients`: Creates a new tenant.
  - **Body**: `{ "name": str, "email": str, "access_token": str, ... }`

### Provisioning
- `POST /provision`: Activates a client on other platforms.
  - **Body**: `{ "client_id": int, "platforms": ["whatsapp", "stock"] }`

### Payments
- `GET /payments/{client_id}`: Returns payment history for a client.
- `POST /payments`: Generates a payment link/QR.
  - **Body**: `{ "client_id": int, "amount": float, "title": str, ... }`

### System
- `GET /commands`: Lists all registered commands available in the registry.
