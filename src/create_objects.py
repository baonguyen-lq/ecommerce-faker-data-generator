import random
from datetime import date, datetime, timedelta
from faker import Faker
import psycopg2
from load_config import load_config

fake = Faker("en_US")

# Default counts (adjust as needed)
COUNTS = {
    "brands": 20,
    "categories": 10,
    "sellers": 25,
    "products": 200,
    "promotions": 10,
    "promotion_products": 100
}

def insert_many(cur, sql, rows):
    cur.executemany(sql, rows)

def generate_and_insert():
    cfg = load_config()
    try:
        with psycopg2.connect(**cfg) as conn:
            with conn.cursor() as cur:
                # 1) Brands
                brands = [(fake.company(), fake.country()) for _ in range(COUNTS["brands"])]
                insert_many(cur,
                    "INSERT INTO brand (brand_name, country) VALUES (%s,%s) RETURNING brand_id;",
                    brands
                )
                cur.execute("SELECT brand_id FROM brand ORDER BY brand_id DESC LIMIT %s;", (COUNTS["brands"],))
                brand_ids = [r[0] for r in cur.fetchall()][::-1]

                # 2) Categories (create a simple parent-child tree)
                categories = []
                parent_ids = [None]
                for i in range(COUNTS["categories"]):
                    parent = random.choice(parent_ids) if i>0 and random.random() < 0.4 else None
                    level = 1 if parent is None else 2
                    categories.append((fake.word().title(), parent, level))
                    if parent is None:
                        parent_ids.append(i+1)  # placeholder; we'll fetch real ids later
                insert_many(cur,
                    "INSERT INTO category (category_name, parent_category_id, level) VALUES (%s,%s,%s) RETURNING category_id;",
                    categories
                )
                cur.execute("SELECT category_id FROM category ORDER BY category_id DESC LIMIT %s;", (COUNTS["categories"],))
                category_ids = [r[0] for r in cur.fetchall()][::-1]

                # 3) Sellers (Vietnam-based)
                sellers = [(fake.company(), fake.date_between(start_date='-3y', end_date='today'), random.choice(["marketplace","direct"]), round(random.uniform(3.0,5.0),1), "Vietnam") for _ in range(COUNTS["sellers"])]
                insert_many(cur,
                    "INSERT INTO seller (seller_name, join_date, seller_type, rating, country) VALUES (%s,%s,%s,%s,%s) RETURNING seller_id;",
                    sellers
                )
                cur.execute("SELECT seller_id FROM seller ORDER BY seller_id DESC LIMIT %s;", (COUNTS["sellers"],))
                seller_ids = [r[0] for r in cur.fetchall()][::-1]

                # 4) Products
                products = []
                for _ in range(COUNTS["products"]):
                    pname = fake.sentence(nb_words=3).rstrip('.')
                    cat = random.choice(category_ids)
                    brand = random.choice(brand_ids)
                    seller = random.choice(seller_ids)
                    price = round(random.uniform(5, 2000), 2)
                    discount = round(price * random.choice([0, 0.05, 0.1, 0.15]), 2) if random.random() < 0.4 else None
                    stock = random.randint(0, 500)
                    rating = round(random.uniform(2.5, 5.0), 1)
                    products.append((pname, cat, brand, seller, price, discount, stock, rating))
                insert_many(cur,
                    """INSERT INTO product
                       (product_name, category_id, brand_id, seller_id, price, discount_price, stock_qty, rating)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING product_id;""",
                    products
                )
                cur.execute("SELECT product_id FROM product ORDER BY product_id DESC LIMIT %s;", (COUNTS["products"],))
                product_ids = [r[0] for r in cur.fetchall()][::-1]

                # 5) Promotions
                promotions = []
                now = datetime.now()
                for _ in range(COUNTS["promotions"]):
                    end = now + timedelta(days=random.randint(7, 90))
                    promotions.append((fake.catch_phrase(), random.choice(["sitewide","category","brand"]), random.choice(["percent","fixed"]), round(random.uniform(5,50),2), end))
                insert_many(cur,
                    "INSERT INTO promotions (promotion_name, promotion_type, discount_type, discount_value, end_date) VALUES (%s,%s,%s,%s,%s) RETURNING promotion_id;",
                    promotions
                )
                cur.execute("SELECT promotion_id FROM promotions ORDER BY promotion_id DESC LIMIT %s;", (COUNTS["promotions"],))
                promo_ids = [r[0] for r in cur.fetchall()][::-1]

                # 6) Promotion -> Product mappings (random)
                promo_products = []
                for _ in range(COUNTS["promotion_products"]):
                    promo_products.append((random.choice(promo_ids), random.choice(product_ids)))
                insert_many(cur,
                    "INSERT INTO promotion_products (promotion_id, product_id) VALUES (%s,%s);",
                    promo_products
                )

        print("Data generation completed successfully.")
    except Exception as e:
        print("Error during data generation:", e)

if __name__ == "__main__":
    generate_and_insert()
