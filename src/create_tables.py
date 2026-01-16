import psycopg2
from load_config import load_config

def create_tables():
    """Create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS brand (
            brand_id SERIAL PRIMARY KEY,
            brand_name VARCHAR(100) NOT NULL,
            country VARCHAR(50) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS category (
            category_id SERIAL PRIMARY KEY,
            category_name VARCHAR(100) NOT NULL,
            parent_category_id INTEGER,
            level SMALLINT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS seller (
            seller_id SERIAL PRIMARY KEY,
            seller_name VARCHAR(150) NOT NULL,
            join_date DATE NOT NULL,
            seller_type VARCHAR(50),
            rating DECIMAL(2,1),
            country VARCHAR(50) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS product (
            product_id SERIAL PRIMARY KEY,
            product_name VARCHAR(200) NOT NULL,
            category_id INT NOT NULL,
            brand_id INT NOT NULL,
            seller_id INT NOT NULL,
            price DECIMAL(12,2) NOT NULL,
            discount_price DECIMAL(12,2),
            stock_qty INT NOT NULL CHECK (stock_qty >= 0),
            rating FLOAT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,

            FOREIGN KEY (category_id) REFERENCES category(category_id) ON DELETE SET NULL ON UPDATE CASCADE,
            FOREIGN KEY (brand_id) REFERENCES brand(brand_id) ON DELETE SET NULL ON UPDATE CASCADE,
            FOREIGN KEY (seller_id) REFERENCES seller(seller_id) ON DELETE SET NULL ON UPDATE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS promotions (
            promotion_id SERIAL PRIMARY KEY,
            promotion_name VARCHAR(100) NOT NULL,
            promotion_type VARCHAR(50) NOT NULL,
            discount_type VARCHAR(20) NOT NULL,
            discount_value NUMERIC(10,2),
            start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            end_date TIMESTAMP NOT NULL  -- No default; set to future date on insert
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS promotion_products (
            promo_product_id SERIAL PRIMARY KEY,
            promotion_id INT NOT NULL,
            product_id INT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (promotion_id) REFERENCES promotions(promotion_id),
            FOREIGN KEY (product_id) REFERENCES product(product_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id SERIAL PRIMARY KEY,
            order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            seller_id INT NOT NULL,
            status VARCHAR(20) NOT NULL CHECK (status IN ('PLACED', 'PAID', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED')),
            total_amount DECIMAL(12,2) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (seller_id) REFERENCES seller(seller_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS order_item (
            order_item_id BIGSERIAL PRIMARY KEY,
            order_id INT NOT NULL,
            product_id INT NOT NULL,
            order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            quantity INTEGER NOT NULL,
            unit_price NUMERIC(10,2) NOT NULL,
            subtotal NUMERIC(12,2) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES product(product_id)
        )"""
    )
    try:
        config = load_config()
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                for command in commands:
                    cur.execute(command)
        print("All tables created successfully!")
    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error: {error}")


if __name__ == '__main__':
    create_tables()