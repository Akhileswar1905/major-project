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
def parse_and_save_html(path, csv_path):
    with open(path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    main_content_div = soup.find_all("div", class_="YJG4Cf")[0]
    # main_content_div = divs[3]

    if main_content_div:
        products = main_content_div.find_all("div", class_="_75nlfW")

        print(f"Found {len(products)} valid products. Processing top 5...")

        # Open CSV file for writing
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)  # Ensure directory exists
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "Product Name",
                "Price",
                "Link",
                "Image",
                "Ratings",
                "Product Reviews Link",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            if len(products) > 1:
                print(f"Found {len(products)} products.")
                i = 0
                links = []
                review_links = []
                for product in products:
                    i+=1
                    if product.find("a", class_="VJA3rP"):
                        product_link = product.find("a", class_="VJA3rP")["href"]
                    else:
                        product_link = product.find("a", class_="CGtC98")["href"]

                    product_link = f"https://www.flipkart.com{product_link}".split("?")[
                        0
                    ]
                    product_review_link = product_link.replace(
                        "/p/", "/product-reviews/"
                    )
                    fetch_with_selenium(product_link,f'html/flipkart-product/{search}_{i}.html')
                    links.append(product_link)
                    review_links.append(product_review_link)
                    if i==5:
                        break
                
                for i in range(5):
                    with open(f'html/flipkart-product/{search}_{i+1}.html', 'r', encoding='utf-8') as file:
                        html_content = file.read()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        main_content_div = soup.find('div', class_='YJG4Cf')
                        print(main_content_div.find('div', class_='Nx9bqj').text.strip())
                        product_name = main_content_div.find('span', class_='VU-ZEz').text.strip()
                        product_price = main_content_div.find('div', class_='Nx9bqj').text.strip()
                        product_img = main_content_div.find('img', class_='DByuf4 IZexXJ jLEJ7H')['src']
                        product_rating = main_content_div.find('div', class_='XQDdHH').text.strip()
                        product_review_link = review_links[i]
                        print(
                            {
                                "Product Name": product_name,
                                "Price": product_price,
                                "Link": links[i],
                                "Image": product_img,
                                "Ratings": product_rating,
                                "Product Reviews Link": product_review_link,
                            })
                        writer.writerow(
                        {
                            "Product Name": product_name,
                            "Price": product_price,
                            "Link": links[i],
                            "Image": product_img,
                            "Ratings": product_rating,
                            "Product Reviews Link": product_review_link,
                        }
                    )


                print(f"Top 5 products saved to {csv_path}")
            else:
                print("No valid products with h2 tags found.")
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
