# 🏗️ System Architecture

## 1. High-Level Flow
The system uses a **Command-Driven Architecture** to ensure that business logic is completely independent of how it is triggered.

**Flow:**
`Interface (Web/API/CLI)` $ightarrow$ `CommandRegistry` $ightarrow$ `BaseCommand` $ightarrow$ `Core Services` $ightarrow$ `External APIs/DB`

## 2. Multi-Tenancy Model
The Hub acts as the **Identity Provider**. 
- **Global Tenant ID**: A unique identifier generated for every client.
- **Provisioning**: The Hub triggers API calls to other platforms to create isolated schemas/accounts using the Global Tenant ID.
- **Billing**: All payment processing is centralized here using Mercado Pago.

## 3. Components
- **Core**:
  - `models.py`: SQLAlchemy models for Clients, Payments, and Subscriptions.
  - `mp_service.py`: Stateless wrapper for Mercado Pago.
  - `hub_service.py`: Integration layer for cross-platform orchestration.
- **Commands**:
  - Encapsulated business logic (e.g., `ProvisionClientCommand`).
- **Interfaces**:
  - `FastAPI`: REST API for the web and other services.
  - `CLI`: Python script for admin tasks.
  - `Web UI`: Vanilla JS dashboard for human management.
