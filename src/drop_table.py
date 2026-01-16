import psycopg2
from load_config import load_config

def drop_all_tables():
    """Drop all tables in the PostgreSQL database with CASCADE to handle dependencies."""
    drop_commands = [
        "DROP TABLE IF EXISTS order_item CASCADE;",
        "DROP TABLE IF EXISTS promotion_products CASCADE;",
        "DROP TABLE IF EXISTS \"order\" CASCADE;",
        "DROP TABLE IF EXISTS orders CASCADE;",
        "DROP TABLE IF EXISTS product CASCADE;",
        "DROP TABLE IF EXISTS promotions CASCADE;",
        "DROP TABLE IF EXISTS seller CASCADE;",
        "DROP TABLE IF EXISTS category CASCADE;",
        "DROP TABLE IF EXISTS brand CASCADE;"
    ]
    try:
        config = load_config()
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                for command in drop_commands:
                    cur.execute(command)
        print("All tables dropped successfully!")
    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error: {error}")

if __name__ == '__main__':
    drop_all_tables()