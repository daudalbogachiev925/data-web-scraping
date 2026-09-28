"""Парсинг сайта с пагинацией и сохранением в CSV."""
import requests
from bs4 import BeautifulSoup
import csv
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def parse_page(url):
    for attempt in range(3):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            logger.warning(f"Попытка {attempt + 1} не удалась: {e}")
            time.sleep(2)
    return None

def extract_books(soup):
    books = []
    for article in soup.find_all("article", class_="product_pod"):
        title = article.h3.a["title"]
        price = article.find("p", class_="price_color").text
        rating = article.p["class"][1]
        books.append({"title": title, "price": price, "rating": rating})
    return books

def main(max_pages=5):
    all_books = []
    for page in range(1, max_pages + 1):
        logger.info(f"Парсинг страницы {page}")
        soup = parse_page(BASE_URL.format(page))
        if soup:
            all_books.extend(extract_books(soup))
        time.sleep(1)

    with open("books.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "rating"])
        writer.writeheader()
        writer.writerows(all_books)

    logger.info(f"Сохранено {len(all_books)} книг")

if __name__ == "__main__":
    main()
