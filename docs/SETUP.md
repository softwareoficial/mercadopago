# 🚀 Payment Gateway Hub - Deployment Guide

## 1. Overview
The Payment Gateway Hub is the central orchestrator for the ecosystem. It manages client identity, billing (Mercado Pago), and provisions access to **WhatsApp Hub** and **Stock Pro**.

## 2. Railway Deployment
The application is configured to run as a standalone service on Railway.

### Configuration
Ensure the following environment variables are set in the Railway Dashboard:
- `DATABASE_URL`: Connection string for PostgreSQL (e.g., `postgresql://user:pass@host:port/db`).
- `MERCADOPAGO_ACCESS_TOKEN`: Your master admin token for MP.
- `WHATSAPP_HUB_URL`: The URL of your deployed WhatsApp Hub service.
- `STOCK_PRO_URL`: The URL of your deployed Stock Pro service.
- `PORT`: Railway will provide this automatically, but the app defaults to `8000`.

### Deployment Process
1. Push the code to your GitHub repository.
2. Connect the repository to Railway.
3. Railway will detect the `Procfile` and start the FastAPI server using `uvicorn`.

## 3. Local Setup for Testing
1. Install dependencies: `pip install -r requirements.txt`
2. Create a `.env` file based on `.env.example`.
3. Run the server: `python src/main.py`
4. Access the API docs: `http://localhost:8000/docs`
5. Open `src/interfaces/web/index.html` in your browser.
