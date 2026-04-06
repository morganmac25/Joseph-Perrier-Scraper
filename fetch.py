import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def fetch_url(url: str) -> str:

    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def extract_product_links(html: str, base_url: str) -> list:
    
    soup = BeautifulSoup(html, "html.parser")

    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        # only English pages
        if not href.startswith("/en/"):
            continue

        if "/champagnes-et-cuvees/" not in href:
            continue

        full_url = urljoin(base_url, href)

        clean_url = full_url.split("?")[0]

        links.add(clean_url)

    return list(links)