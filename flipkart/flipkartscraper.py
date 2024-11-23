from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
from bs4 import BeautifulSoup
import csv
import os


# Function to fetch HTML with Selenium and save to a file
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


# Function to parse HTML and save data to a CSV file
def parse_and_save_html(file_path, csv_path):
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    main_content_div = soup.find_all("div", class_="YJG4Cf")[0]
    # main_content_div = divs[3]

    if main_content_div:
        products = main_content_div.find_all("div", class_="_75nlfW")
        print(len(products[0]))

        # # Process only the top 5 products with h2 tags
        # if valid_products:
        #     print(f"Found {len(valid_products)} valid products. Processing top 5...")

        #     # Open CSV file for writing
        #     os.makedirs(
        #         os.path.dirname(csv_path), exist_ok=True
        #     )  # Ensure directory exists
        #     with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        #         fieldnames = [
        #             "Product Name",
        #             "Price",
        #             "Link",
        #             "Image",
        #             "Ratings",
        #             "Product Reviews Link",
        #         ]
        #         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        #         writer.writeheader()

        #         for product in valid_products[:5]:  # Process top 5 products
        #             link = product.find("a", class_="a-link-normal")["href"]
        #             product_link = f"https://www.flipkart.com{link}"
        #             product_name = product.find("h2").text.strip()

        #             img_holder = product.find("div", class_="s-product-image-container")
        #             product_img = img_holder.find("img")["src"] if img_holder else "N/A"

        #             product_price = product.find("span", class_="a-offscreen")
        #             product_price = (
        #                 product_price.text.strip() if product_price else "N/A"
        #             )

        #             product_ratings = product.find("span", class_="a-icon-alt")
        #             product_ratings = (
        #                 product_ratings.text.strip() if product_ratings else "N/A"
        #             )

        #             # Write the product data to the CSV
        #             writer.writerow(
        #                 {
        #                     "Product Name": product_name,
        #                     "Price": product_price,
        #                     "Link": product_link,
        #                     "Image": product_img,
        #                     "Ratings": product_ratings,
        #                     "Product Reviews Link": f"http://www.flipkart.com/product-reviews/{link.split('/')[3]}",
        #                 }
        #             )

        #     print(f"Top 5 products saved to {csv_path}")
        # else:
        #     print("No valid products with h2 tags found.")
    else:
        print("Div with class 's-search-results' not found.")


# Main execution
search = input("Enter the product name: ")

url = f"https://www.flipkart.com/search?q={search}"
path = f"html/{search}.html"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

csv_path = f"data/{search}_{timestamp}.csv"

fetch_with_selenium(url, path)
parse_and_save_html(path, csv_path)
