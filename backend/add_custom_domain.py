#!/usr/bin/env python3
"""
Migration script to add custom_domain column to shopify_stores table
Run this once to update existing database
"""

from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate():
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        # Check if column already exists
        if settings.DATABASE_URL.startswith("sqlite"):
            result = conn.execute(text("PRAGMA table_info(shopify_stores)"))
            columns = [row[1] for row in result.fetchall()]
            if 'custom_domain' in columns:
                print("Column 'custom_domain' already exists")
                return

            conn.execute(text("ALTER TABLE shopify_stores ADD COLUMN custom_domain VARCHAR"))
        else:
            # PostgreSQL
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'shopify_stores' AND column_name = 'custom_domain'
            """))
            if result.fetchone():
                print("Column 'custom_domain' already exists")
                return

            conn.execute(text("ALTER TABLE shopify_stores ADD COLUMN custom_domain VARCHAR"))

        conn.commit()
        print("Successfully added 'custom_domain' column to shopify_stores table")

if __name__ == "__main__":
    migrate()
