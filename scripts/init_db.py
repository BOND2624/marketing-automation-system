"""Initialize the database with tables."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import Base, engine
from core.config import get_settings

settings = get_settings()


def init_database():
    """Create all database tables."""
    print(f"Initializing database: {settings.database_url}")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    init_database()

