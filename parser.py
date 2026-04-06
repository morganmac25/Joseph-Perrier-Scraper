from bs4 import BeautifulSoup
import uuid
from urllib.parse import urljoin


def parse_listing_page(html: str, base_url: str) -> list:
    soup = BeautifulSoup(html, "html.parser")

    products = []

    items = soup.select('div[data-elementor-type="loop-item"]')

    for item in items:
        link_tag = item.find("a", href=True)
        name_tag = item.select_one(".elementor-heading-title")
        img_tag = item.find("img")

        if not link_tag:
            continue

        url = urljoin(base_url, link_tag["href"])
        name = name_tag.text.strip().title() if name_tag else "Unknown"

        image = None
        if img_tag and img_tag.get("src"):
            image = urljoin(base_url, img_tag["src"])

        products.append({
            "url": url,
            "name": name,
            "image": image
        })

    return products


def parse_product_page(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # name
    name_tag = soup.select_one("h1, h2, .title")
    name = name_tag.text.strip().title() if name_tag else "Unknown"

    if not name or name == "Unknown":
        return None

    # desceiption
    description = ""
    # Only consider inside  elementor-widget-container
    for p in soup.select("div.elementor-widget-container p"):
        text = p.get_text(strip=True)
        if not text:
            continue

        description = text
        break

    # type filtering
    lower_name = name.lower()
    if "brut nature" in lower_name:
        wine_type = "Brut Nature"
    elif "brut" in lower_name:
        wine_type = "Brut"
    elif "rosé" in lower_name or "rose" in lower_name:
        wine_type = "Rosé"
    elif "blanc de blancs" in lower_name:
        wine_type = "Blanc de Blancs"
    elif "demi-sec" in lower_name:
        wine_type = "Demi-Sec"
    elif "vintage" in lower_name:
        wine_type = "Vintage"
    else:
        wine_type = "Unknown"

    # images
    images = []

    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue

        # keep real product images
        if any(x in src.lower() for x in [
            "cuvee",
            "bottle",
            "sans_ombre"
        ]) and not any(x in src.lower() for x in [
            "logo",
            "icon",
            "facebook",
            "linkedin",
            "svg",
            "menu",
            "badge"
        ]):
            images.append(src)

    # remove duplicates
    images = list(set(images))

    # videos
    videos = []

    for iframe in soup.find_all("iframe"):
        src = iframe.get("src")
        if not src:
            continue

        # ONLY keep real video embeds
        if "youtube" in src or "vimeo" in src:
            videos.append(src)

    videos = list(set(videos))

    return {
        "product": {
            "id": str(uuid.uuid4()),
            "name": name,
            "type": wine_type,
            "description": description,
            "winery_id": "default-winery-id",
            "source_url": url
        },
        "media": [
            {
                "id": str(uuid.uuid4()),
                "url": m,
                "type": "image",
                "product_id": None,
                "winery_id": None
            } for m in images
        ] + [
            {
                "id": str(uuid.uuid4()),
                "url": v,
                "type": "video",
                "product_id": None,
                "winery_id": None
            } for v in videos
        ]
    }