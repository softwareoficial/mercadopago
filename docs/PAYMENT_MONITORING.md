# Global Payment Monitoring System

## Overview
The Global Payment Monitoring system allows administrators to track all payment attempts and their statuses across all tenants (clients) in the platform. This provides a centralized view to identify which clients have completed their payments and which are still pending.

## Backend Implementation

### 1. Commands
The business logic is encapsulated in the following commands located in `src/commands/payment_cmds/`:

- **`ListAllPaymentsCommand`**:
    - **Purpose**: Fetches all payments from the database, joining them with the `Client` model to include the client's name.
    - **Registry Key**: `payment:all`
    - **Returns**: A list of payment objects including `id`, `client_name`, `amount`, `status`, and `created_at`.

- **`UpdatePaymentStatusCommand`**:
    - **Purpose**: Updates the status of a specific payment. This is used to simulate the result of a Mercado Pago webhook notification.
    - **Registry Key**: `payment:update_status`
    - **Params**: `payment_id` (int), `status` (string: `pending`, `approved`, `rejected`).

### 2. API Endpoints
The following routes were added to `src/interfaces/api/routes.py`:

| Endpoint | Method | Description | Command Used |
| :--- | :--- | :--- | :--- |
| `/payments/all` | `GET` | Lists all payments across all clients | `payment:all` |
| `/payments/<id>/status` | `PATCH` | Updates the status of a payment | `payment:update_status` |

## Frontend Implementation

### 1. UI Changes
- **Sidebar**: A new link **"Pagos Globales"** was added to the main navigation.
- **Main Content**: A new section `section-global_payments` was created, featuring a table that displays:
    - Payment ID
    - Client Name
    - Amount
    - Status (Color-coded: Green for `approved`, Yellow for others)
    - Date

### 2. JavaScript Logic (`src/interfaces/web/js/app.js`)
- **`showSection('global_payments')`**: Handles the visibility of the global payments section and hides the client selector since this is an administrative view.
- **`loadGlobalPayments()`**: Fetches data from `/payments/all` and populates the global payments table.

## Simulation Guide (Testing Flow)

To test the payment and notification flow manually:

1. **Start the Server**:
   ```bash
   $env:PYTHONPATH='.'; python src/main.py
   ```

2. **Create a Payment**:
   Use `curl` or the Admin Panel to create a payment for a specific client.
   ```bash
   curl.exe -X POST "http://localhost:9000/payments" -H "Content-Type: application/json" -d "{"client_id":2,"amount":100.0,"title":"Test","description":"Test"}"
   ```
   *Note the `payment_id` returned (e.g., #5).*

3. **Simulate Payment Approval**:
   Update the status of the created payment to simulate a successful Mercado Pago notification.
   ```bash
   curl.exe -X PATCH "http://localhost:9000/payments/5/status" -H "Content-Type: application/json" -d "{"status":"approved"}"
   ```

4. **Verify in Admin Panel**:
   Navigate to **Pagos Globales** in the browser to see the payment status updated to **approved**.
