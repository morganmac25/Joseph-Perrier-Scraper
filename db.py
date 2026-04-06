import sqlite3

DB_NAME = "wine.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS winery (
        id TEXT PRIMARY KEY,
        name TEXT,
        description TEXT,
        location TEXT,
        founded_year INTEGER,
        website TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product (
        id TEXT PRIMARY KEY,
        name TEXT,
        type TEXT,
        description TEXT,
        grape_variety TEXT,
        dosage TEXT,
        aging TEXT,
        winery_id TEXT,
        FOREIGN KEY (winery_id) REFERENCES winery(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS media (
        id TEXT PRIMARY KEY,
        url TEXT,
        type TEXT,
        product_id TEXT,
        winery_id TEXT,
        FOREIGN KEY (product_id) REFERENCES product(id),
        FOREIGN KEY (winery_id) REFERENCES winery(id)
    );
    """)

def insert_media(cursor, media: dict):
    cursor.execute("""
    INSERT INTO media (id, url, type, product_id, winery_id)
    VALUES (?, ?, ?, ?, ?)
    """, (
        media["id"],
        media["url"],
        media["type"],
        media.get("product_id"),
        media.get("winery_id")
    ))


def insert_winery(cursor, winery: dict):
    cursor.execute("""
    INSERT OR IGNORE INTO winery (id, name, description, location, founded_year, website)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        winery["id"],
        winery["name"],
        winery.get("description"),
        winery.get("location"),
        winery.get("founded_year"),
        winery.get("website")
    ))


def insert_product(cursor, product: dict):
    cursor.execute("""
    INSERT INTO product (id, name, type, description, winery_id)
    VALUES (?, ?, ?, ?, ?)
    """, (
        product["id"],
        product["name"],
        product.get("type"),
        product.get("description"),
        product.get("winery_id")
    ))


def get_all_products(cursor):
    cursor.execute("SELECT name FROM product")
    return cursor.fetchall()

def get_products_with_media(cursor):
    cursor.execute("""
    SELECT p.name, m.url, m.type
    FROM product p
    LEFT JOIN media m ON p.id = m.product_id
    """)
    return cursor.fetchall()

def get_products_with_media(cursor):
    cursor.execute("""
    SELECT 
        p.name,
        p.type,
        p.description,
        m.url,
        m.type
    FROM product p
    LEFT JOIN media m ON p.id = m.product_id
    ORDER BY p.name
    """)
    return cursor.fetchall()

def clear_tables(cursor, confirm=False):
    """
    Delete all data from tables (but keep schema).
    Order matters because of foreign keys.
    """

    if not confirm:
        print("Skipping DB clear (confirm=False)")
        return
    
    cursor.execute("DELETE FROM media;")
    cursor.execute("DELETE FROM product;")
    cursor.execute("DELETE FROM winery;")