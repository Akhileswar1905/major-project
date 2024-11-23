from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
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
    main_content_div = soup.find("div", id="main-content")

    if main_content_div:
        products = main_content_div.find_all("div", class_="rilrtl-products-list__item")

        if products:
            # Open CSV file for writing
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Product Name", "Price", "Link", "Image", "Ratings"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for i in range(
                    min(5, len(products))
                ):  # Only process the first 5 products
                    product = products[i]
                    product_link = (
                        "https://ajio.com"
                        + product.find("a", class_="rilrtl-products-list__link")["href"]
                    )
                    product_name = product.find("div", class_="nameCls").text.strip()

                    imgHolder = product.find("div", class_="imgHolder")
                    if imgHolder and imgHolder.find("img").has_attr("src"):
                        product_img = imgHolder.find("img")["src"]
                    else:
                        product_img = "No image available"

                    product_price = product.find("span", class_="price").text.strip()
                    product_ratings = product.find("p", class_="_3I65V")
                    product_ratings = (
                        product_ratings.text.strip()
                        if product_ratings
                        else "No ratings"
                    )

                    # Write the product data to the CSV
                    writer.writerow(
                        {
                            "Product Name": product_name,
                            "Price": product_price,
                            "Link": product_link,
                            "Image": product_img,
                            "Ratings": product_ratings,
                        }
                    )
            print(f"Data saved to {csv_path}")
        else:
            print("No products found.")
    else:
        print("Div with id 'main-content' not found.")


# Main execution
search = input("Enter the product name: ")

url = f"https://www.ajio.com/search/?text={search}"
path = f"html/{search}.html"
csv_path = f"data/{search}_products.csv"

fetch_with_selenium(url, path)
parse_and_save_html(path, csv_path)
