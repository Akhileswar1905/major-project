from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
from bs4 import BeautifulSoup
import csv
import os


# Function to fetch HTML using Selenium
def fetch_with_selenium(url, path):
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)
    time.sleep(5)

    html = driver.page_source

    os.makedirs(os.path.dirname(path), exist_ok=True)  # Ensure the directory exists
    with open(path, "w", encoding="utf-8") as file:
        file.write(html)

    driver.quit()


# Ajio Scraper
def scrape_ajio(search):
    url = f"https://www.ajio.com/search/?text={search}"
    path = f"html/ajio_{search}.html"
    csv_path = f"data/ajio_{search}.csv"
    fetch_with_selenium(url, path)

    with open(path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    main_content_div = soup.find("div", id="main-content")

    if main_content_div:
        products = main_content_div.find_all("div", class_="rilrtl-products-list__item")

        if products:
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Product Name", "Price", "Link", "Image", "Ratings"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for product in products[:5]:  # Top 5 products
                    product_link = (
                        "https://ajio.com"
                        + product.find("a", class_="rilrtl-products-list__link")["href"]
                    )
                    product_name = product.find("div", class_="nameCls").text.strip()
                    product_img = product.find("div", class_="imgHolder").find("img")[
                        "src"
                    ]
                    product_price = product.find("span", class_="price").text.strip()
                    product_ratings = product.find("p", class_="_3I65V")
                    product_ratings = (
                        product_ratings.text.strip()
                        if product_ratings
                        else "No ratings"
                    )

                    writer.writerow(
                        {
                            "Product Name": product_name,
                            "Price": product_price,
                            "Link": product_link,
                            "Image": product_img,
                            "Ratings": product_ratings,
                        }
                    )
            print(f"Ajio data saved to {csv_path}")
        else:
            print("No products found on Ajio.")
    else:
        print("Main content not found on Ajio.")


# Amazon Scraper
def scrape_amazon(search):
    url = f"https://www.amazon.in/search/s?k={search}"
    path = f"html/amazon_{search}.html"
    csv_path = f"data/amazon_{search}.csv"
    fetch_with_selenium(url, path)

    with open(path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    main_content_div = soup.find("div", class_="s-search-results")

    if main_content_div:
        products = main_content_div.find_all("div", class_="puisg-row")
        valid_products = [product for product in products if product.find("h2")]

        if valid_products:
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Product Name", "Price", "Link", "Image", "Ratings"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for product in valid_products[:5]:  # Top 5 products
                    link = product.find("a", class_="a-link-normal")["href"]
                    product_link = f"https://www.amazon.in{link}"
                    product_name = product.find("h2").text.strip()
                    product_img = product.find("img")["src"]
                    product_price_holder = product.find("span", class_="a-price")
                    product_price = product_price_holder.find(
                        "span", class_="a-offscreen"
                    ).text.strip()
                    product_ratings = product.find("span", class_="a-icon-alt")
                    product_ratings = (
                        product_ratings.text.strip() if product_ratings else "N/A"
                    )

                    writer.writerow(
                        {
                            "Product Name": product_name,
                            "Price": product_price,
                            "Link": product_link,
                            "Image": product_img,
                            "Ratings": product_ratings,
                        }
                    )
            print(f"Amazon data saved to {csv_path}")
        else:
            print("No valid products found on Amazon.")
    else:
        print("Search results not found on Amazon.")


# Flipkart Scraper
def scrape_flipkart(search):
    url = f"https://www.flipkart.com/search?q={search}"
    path = f"html/flipkart_{search}.html"
    csv_path = f"data/flipkart_{search}.csv"
    fetch_with_selenium(url, path)

    with open(path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    main_content_div = soup.find_all("div", class_="YJG4Cf")[0]

    if main_content_div:
        products = main_content_div.find_all("div", class_="_75nlfW")

        if products:
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Product Name", "Price", "Link", "Image", "Ratings"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for product in products[:5]:  # Top 5 products
                    product_name = product.find("a", class_="WKTcLC").text.strip()
                    product_price = product.find("div", class_="Nx9bqj").text.strip()
                    product_rating = product.find("div", class_="_3LWZlK")
                    product_rating = (
                        product_rating.text.strip() if product_rating else "No ratings"
                    )
                    product_link = product.find("a", class_="WKTcLC")["href"]
                    product_img = product.find("img", class_="_53J4C-")["src"]

                    writer.writerow(
                        {
                            "Product Name": product_name,
                            "Price": product_price,
                            "Link": f"https://www.flipkart.com{product_link}",
                            "Image": product_img,
                            "Ratings": product_rating,
                        }
                    )
            print(f"Flipkart data saved to {csv_path}")
        else:
            print("No products found on Flipkart.")
    else:
        print("Main content not found on Flipkart.")


# Main execution
if __name__ == "__main__":
    search = input("Enter the product name: ")
    scrape_ajio(search)
    scrape_amazon(search)
    scrape_flipkart(search)
