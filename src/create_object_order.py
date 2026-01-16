import random
from datetime import datetime, timedelta
from decimal import Decimal
from faker import Faker
import psycopg2
from psycopg2.extras import execute_batch
from load_config import load_config

fake = Faker("en_US")

# Configuration
MIN_ORDERS = 2_500_000
MAX_ORDERS = 3_000_000
ITEMS_PER_ORDER_MIN = 2
ITEMS_PER_ORDER_MAX = 4
BATCH_SIZE = 10_000
# Date range (August 1, 2025 to October 31, 2025)
START_DATE = datetime(2025, 8, 1)
END_DATE = datetime(2025, 10, 31)

# Status distribution (mapping to table's allowed values)
# 80% 'DELIVERED' (as 'completed'), 10% 'CANCELLED', 10% 'PLACED' (as 'pending')
STATUS_WEIGHTS = ['DELIVERED'] * 8 + ['CANCELLED'] * 1 + ['PLACED'] * 1

def random_date(start, end):
    """Generate a random datetime between start and end."""
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)

def generate_orders_and_items():
    cfg = load_config()
    try:
        with psycopg2.connect(**cfg) as conn:
            with conn.cursor() as cur:
                # Fetch all sellers
                cur.execute("SELECT seller_id FROM seller;")
                seller_ids = [row[0] for row in cur.fetchall()]
                if not seller_ids:
                    raise ValueError("No sellers found. Populate seller table first.")

                # Fetch products grouped by seller
                cur.execute("""
                    SELECT seller_id, array_agg(product_id) AS product_ids,
                           array_agg(price) AS prices,
                           array_agg(discount_price) AS discount_prices
                    FROM product
                    GROUP BY seller_id;
                """)
                products_by_seller = {}
                for row in cur.fetchall():
                    seller_id, prod_ids, prices, disc_prices = row
                    # Ensure disc_prices handles None values
                    disc_prices = [d if d is not None else None for d in disc_prices]
                    products_by_seller[seller_id] = list(zip(prod_ids, prices, disc_prices))

                if not products_by_seller:
                    raise ValueError("No products found. Populate product table first.")

                # Decide total orders
                total_orders = random.randint(MIN_ORDERS, MAX_ORDERS)
                print(f"Generating {total_orders} orders...")

                order_batch = []
                order_item_batch = []
                items_for_batch = []  # To hold items temporarily for the batch

                for order_num in range(total_orders):
                    # Select random seller
                    seller_id = random.choice(seller_ids)

                    # Random order_date
                    order_date = random_date(START_DATE, END_DATE)

                    # Random status
                    status = random.choice(STATUS_WEIGHTS)

                    # Select 2-4 products from this seller
                    available_products = products_by_seller.get(seller_id, [])
                    if len(available_products) < ITEMS_PER_ORDER_MIN:
                        continue  # Skip if not enough products (rare)

                    num_items = random.randint(ITEMS_PER_ORDER_MIN, ITEMS_PER_ORDER_MAX)
                    selected_items = random.sample(available_products, min(num_items, len(available_products)))

                    # Calculate total_amount and prepare order_items
                    total_amount = Decimal('0')
                    this_order_items = []
                    for product_id, price, discount_price in selected_items:
                        quantity = random.randint(1, 5)  # Assume 1-5 units per item
                        unit_price = Decimal(discount_price) if discount_price is not None else Decimal(price)
                        subtotal = Decimal(quantity) * unit_price  # Ensure Decimal multiplication
                        total_amount += subtotal
                        this_order_items.append((product_id, quantity, unit_price, subtotal, order_date))

                    # Add to order batch
                    order_batch.append((order_date, seller_id, status, total_amount))
                    items_for_batch.append(this_order_items)

                    # Batch insert orders if ready
                    if len(order_batch) >= BATCH_SIZE or order_num == total_orders - 1:
                        # Insert orders and get order_ids using execute_batch
                        order_sql = """
                            INSERT INTO orders (order_date, seller_id, status, total_amount)
                            VALUES (%s, %s, %s, %s)
                            RETURNING order_id;
                        """
                        execute_batch(cur, order_sql, order_batch)
                        new_order_ids = [row[0] for row in cur.fetchall()]

                        # Now assign order_items with real order_ids
                        for i, oid in enumerate(new_order_ids):
                            this_order_items = items_for_batch[i]
                            for product_id, quantity, unit_price, subtotal, order_date in this_order_items:
                                order_item_batch.append((oid, product_id, order_date, quantity, unit_price, subtotal))

                        # Batch insert order_items if ready
                        if len(order_item_batch) >= BATCH_SIZE * 3 or order_num == total_orders - 1:  # Roughly, since more items
                            item_sql = """
                                INSERT INTO order_item (order_id, product_id, order_date, quantity, unit_price, subtotal)
                                VALUES (%s, %s, %s, %s, %s, %s);
                            """
                            execute_batch(cur, item_sql, order_item_batch)
                            order_item_batch = []

                        order_batch = []
                        items_for_batch = []

                # Final insert for any remaining order_items
                if order_item_batch:
                    item_sql = """
                        INSERT INTO order_item (order_id, product_id, order_date, quantity, unit_price, subtotal)
                        VALUES (%s, %s, %s, %s, %s, %s);
                    """
                    execute_batch(cur, item_sql, order_item_batch)

        print("Order and order_item data generation completed successfully.")
        print(f"Generated approximately {total_orders * (ITEMS_PER_ORDER_MIN + ITEMS_PER_ORDER_MAX) / 2} order items.")

    except Exception as e:
        print("Error during order data generation:", e)

if __name__ == "__main__":
    generate_orders_and_items()