import os
from src.interfaces.api.routes import app
from src.core.db import init_db
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # Initialize DB tables
    init_db()
    
    port = int(os.getenv("PORT", 9000))
    print(f"🚀 Starting Payment Gateway API server (Flask Mode) on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
