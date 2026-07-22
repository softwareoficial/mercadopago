import argparse
import sys
from sqlalchemy.orm import Session
from src.core.db import SessionLocal, init_db
from src.commands.registry import CommandRegistry

def main():
    init_db()
    db = SessionLocal()

    parser = argparse.ArgumentParser(description="Payment Gateway CLI - Admin Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Client Create Command ---
    client_parser = subparsers.add_parser("client:create", help="Create a new client")
    client_parser.add_argument("--name", required=True, help="Client name")
    client_parser.add_argument("--email", required=True, help="Client email")
    client_parser.add_argument("--token", required=True, help="Mercado Pago Access Token")
    client_parser.add_argument("--pubkey", help="Public Key")
    client_parser.add_argument("--cid", help="Client ID")
    client_parser.add_argument("--secret", help="Client Secret")
    client_parser.add_argument("--webhook", help="Webhook Secret")

    # --- Payment Create Command ---
    pay_parser = subparsers.add_parser("payment:create", help="Create a payment link")
    pay_parser.add_argument("--client", type=int, required=True, help="Client ID")
    pay_parser.add_argument("--amount", type=float, required=True, help="Amount")
    pay_parser.add_argument("--title", required=True, help="Product Title")
    pay_parser.add_argument("--desc", default="", help="Description")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        cmd = CommandRegistry.get_command(args.command)
        
        # Map CLI args to Command kwargs
        kwargs = {}
        if args.command == "client:create":
            kwargs = {
                "name": args.name,
                "email": args.email,
                "access_token": args.token,
                "public_key": args.pubkey,
                "client_id": args.cid,
                "client_secret": args.secret,
                "webhook_secret": args.webhook
            }
        elif args.command == "payment:create":
            kwargs = {
                "client_id": args.client,
                "amount": args.amount,
                "title": args.title,
                "description": args.desc
            }

        result = cmd.execute(db=db, **kwargs)
        print(f"✅ Success: {result}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
