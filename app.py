from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
from bs4 import BeautifulSoup
import csv
import os
from flask import Flask

app = Flask(__name__)

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
@app.route('/ajio_scraper/<search>', methods=['GET'])
def scrape_ajio(search):
    url = f"https://www.ajio.com/search/?text={search}"
    path = f"html/ajio_{search}.html"
    csv_path = f"data/ajio_{search}.csv"
    fetch_with_selenium(url, path)
    results = []
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

                    results.append({
                        "Product Name": product_name,
                        "Price": product_price,
                        "Link": product_link,
                        "Image": product_img,
                        "Ratings": product_ratings,
                    })
            print(f"Ajio data saved to {csv_path}")
        else:
            print("No products found on Ajio.")
    else:
        print("Main content not found on Ajio.")
    return {
        "results": results,
    }

# Amazon Scraper

@app.route('/amazon_scraper/<search>', methods=['GET'])
def scrape_amazon(search):
    url = f"https://www.amazon.in/search/s?k={search}"
    path = f"html/amazon_{search}.html"
    csv_path = f"data/amazon_{search}.csv"
    fetch_with_selenium(url, path)
    results = []
    with open(path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    main_content_div = soup.find("div", class_="s-search-results")

    if main_content_div:
        products = main_content_div.find_all("div", class_="puisg-row")
        valid_products = [product for product in products if product.find("h2")]

        if valid_products:
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Product Name", "Price", "Link", "Image", "Ratings", "Review Link"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for product in valid_products[:5]:  # Top 5 products
                    link = product.find("a", class_="a-link-normal")["href"]
                    product_link = f"https://www.amazon.in{link}"
                    product_id = link.split("/")[3]
                    reviews_link = f"https://www.amazon.in/product-reviews/{product_id}"
                    reviews_path = f"html/product-reviews/{product_id}.html"
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
                            "Reviewe link": reviews_link,
                        }
                    )

                    results.append({
                        "Product Name": product_name,
                        "Price": product_price,
                        "Link": product_link,
                        "Image": product_img,
                        "Ratings": product_ratings,
                            "Reviewe link": reviews_link,

                    })
            print(f"Amazon data saved to {csv_path}")
        else:
            print("No valid products found on Amazon.")
    else:
        print("Search results not found on Amazon.")

    return {
        "results": results,
    }

# Flipkart Scraper

@app.route('/flipkart_scraper/<search>', methods=['GET'])
def scrape_flipkart(search):
    url = f"https://www.flipkart.com/search?q={search}"
    path = f"html/flipkart_{search}.html"
    csv_path = f"data/flipkart_{search}.csv"
    fetch_with_selenium(url, path)
    results = []
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
                        results.append(
                            {"Product Name": product_name,
                            "Price": product_price,
                            "Link": links[i],
                            "Image": product_img,
                            "Ratings": product_rating,
                            "Product Reviews Link": product_review_link,
                            })


                print(f"Top 5 products saved to {csv_path}")
            else:
                print("No valid products with h2 tags found.")
    else:
        print("Div with class 's-search-results' not found.")

    return {
        "results": results,
    }

# Main execution
# if __name__ == "__main__":
#     search = input("Enter the product name: ")
#     scrape_ajio(search)
#     scrape_amazon(search)
#     scrape_flipkart(search)

# Run the app
if __name__ == "__main__":
    app.run()
