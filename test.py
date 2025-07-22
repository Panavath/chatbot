import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("❌ DATABASE_URL is missing in .env file")
else:
    print(f"🔗 Connecting to: {database_url}")

    try:
        engine = sqlalchemy.create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES;"))
            tables = result.fetchall()
            print("✅ Connection successful! Tables found:", tables if tables else "No tables found.")
    except Exception as e:
        print("❌ Connection failed:", str(e))
