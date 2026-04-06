from fetch import fetch_url
from parser import parse_listing_page, parse_product_page
from db import (
    get_connection,
    create_tables,
    insert_winery,
    insert_product,
    insert_media,
    get_products_with_media
)

import uuid

LISTING_URL = "https://www.josephperrier.com/en/champagnes-cuvees/?v=0b3b97fa6688"
BASE_URL = "https://www.josephperrier.com"


def main():
    conn = get_connection()
    cursor = conn.cursor()

    create_tables(cursor)

    winery_id = "default-winery-id"

    insert_winery(cursor, {
        "id": winery_id,
        "name": "Joseph Perrier",
        "description": None,
        "location": "France",
        "founded_year": 1825,
        "website": BASE_URL
    })

    # fetch
    listing_html = fetch_url(LISTING_URL)

    # parse
    products = parse_listing_page(listing_html, BASE_URL)

    print(f"Found {len(products)} products")

    # deupe
    seen = set()
    unique_products = []

    for p in products:
        if p["url"] not in seen:
            seen.add(p["url"])
            unique_products.append(p)

    products = unique_products

    print(f"After dedupe: {len(products)} products")

    # product scrape
    for p in products:
        try:
            print("Scraping:", p["name"])

            html = fetch_url(p["url"])
            parsed = parse_product_page(html, p["url"])

            if not parsed:
                print("Skipping:", p["url"])
                continue

            product = parsed["product"]
            media_items = parsed["media"]

            product["name"] = p["name"]

            insert_product(cursor, product)

            # Add listing image
            if p.get("image"):
                insert_media(cursor, {
                    "id": str(uuid.uuid4()),
                    "url": p["image"],
                    "type": "image",
                    "product_id": product["id"],
                    "winery_id": None
                })

            # Add product page media
            for m in media_items:
                m["product_id"] = product["id"]
                insert_media(cursor, m)

            print("Inserted:", product["name"])

        except Exception as e:
            print(f"Error scraping {p['url']}: {e}")

    conn.commit()

    # inspect
    print("\nDetailed product view:\n")

    rows = get_products_with_media(cursor)

    current_product = None

    for name, wine_type, desc, media_url, media_type in rows:
        if name != current_product:
            print("\n========================")
            print("Name:", name)
            print("Type:", wine_type)
            print("Description:", (desc[:100] + "...") if desc else "")
            print("Media:")
            current_product = name

        if media_url:
            print(f"  - [{media_type}] {media_url}")


if __name__ == "__main__":
    main()