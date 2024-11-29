from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os
import csv

# Function to fetch HTML with Selenium and save it to a file
def fetch_with_selenium(url, path):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )  # Wait for the page to load

    html = driver.page_source
    os.makedirs(os.path.dirname(path), exist_ok=True)  # Ensure directory exists
    with open(path, "w", encoding="utf-8") as file:
        file.write(html)

    driver.quit()

# Function to parse HTML and save data to a CSV file
def parse_and_save_html(file_path, csv_path):
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    main_content_div = soup.find("div", class_="s-search-results")

    if main_content_div:
        products = main_content_div.find_all("div", class_="sg-col-inner")
        valid_products = [
            product for product in products if product.find("h2")
        ]  # Filter products with h2 tags

        if valid_products:
            print(f"Found {len(valid_products)} valid products. Processing top 5...")

            os.makedirs(os.path.dirname(csv_path), exist_ok=True)  # Ensure directory exists
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
                    "Product Name",
                    "Price",
                    "Link",
                    "Image",
                    "Ratings",
                    "Product Reviews Link",
                    "Reviews",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for product in valid_products[:5]:  # Process top 5 products
                    link_tag = product.find("a", class_="a-link-normal")
                    if not link_tag:
                        continue
                    
                    link = link_tag["href"]
                    product_link = f"https://www.amazon.in{link}"
                    product_name = product.find("h2").text.strip()

                    img_holder = product.find("img")
                    product_img = img_holder["src"] if img_holder else "N/A"

                    product_price = product.find("span", class_="a-offscreen")
                    product_price = (
                        product_price.text.strip() if product_price else "N/A"
                    )

                    product_ratings = product.find("span", class_="a-icon-alt")
                    product_ratings = (
                        product_ratings.text.strip() if product_ratings else "N/A"
                    )

                    # Scrape reviews from the product reviews page
                    try:
                        product_id = link.split("/")[3]
                        reviews_link = f"https://www.amazon.in/product-reviews/{product_id}"
                        reviews_path = f"html/product-reviews/{product_id}.html"
                        print(reviews_link)
                        fetch_with_selenium(reviews_link, reviews_path)

                        # Parse the reviews page
                        reviews = []
                        with open(reviews_path, "r", encoding="utf-8") as review_file:
                            reviews_html = review_file.read()
                            review_soup = BeautifulSoup(reviews_html, "html.parser")
                            review_div = review_soup.find('div', id="cm_cr-review_list")
                            print(review_soup.find('div', class_='reviews-views'))
                            review_spans = review_div.find_all(
                                "span", class_="a-size-base review-text review-text-content"
                            )
                            reviews = [review.text.strip() for review in review_spans]
                            print(reviews)
                    except Exception as e:
                        print(f"Error fetching reviews for {product_name}: {e}")
                        reviews = []

                    # Write product data to the CSV
                    writer.writerow(
                        {
                            "Product Name": product_name,
                            "Price": product_price,
                            "Link": product_link,
                            "Image": product_img,
                            "Ratings": product_ratings,
                            "Product Reviews Link": reviews_link,
                            "Reviews": " | ".join(reviews),
                        }
                    )

            print(f"Top 5 products saved to {csv_path}")
        else:
            print("No valid products with h2 tags found.")
    else:
        print("Div with class 's-search-results' not found.")

# Main execution
search = input("Enter the product name: ")
url = f"https://www.amazon.in/s?k={search}"
path = f"html/{search}.html"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_path = f"data/{search}_{timestamp}.csv"

fetch_with_selenium(url, path)
parse_and_save_html(path, csv_path)
