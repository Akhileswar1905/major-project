import json
import scrapy
from urllib.parse import urljoin
import os
from datetime import datetime


class FlipkartscraperSpider(scrapy.Spider):
    name = "flipkartscraper"
    allowed_domains = ["www.flipkart.com"]
    start_urls = ["https://www.flipkart.com/"]

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    def __init__(self, *args, **kwargs):
        super(FlipkartscraperSpider, self).__init__(*args, **kwargs)

        # Create 'data' directory if it doesn't exist
        if not os.path.exists("data"):
            os.makedirs("data")

        # Modify the output file name dynamically based on the product name
        self.file_name = None  # Placeholder for the final file name

    def start_requests(self):
        keyword_list = input("ENTER THE PRODUCT NAME: ").strip().split(",")

        # Update the file name based on the first keyword
        product_name = "_".join(keyword_list).replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.file_name = (
            f"data/{product_name}_{timestamp}.json"  # Save in 'data' folder
        )

        for keyword in keyword_list:
            flipkart_search_url = f"https://www.flipkart.com/search?q={keyword}"
            yield scrapy.Request(
                url=flipkart_search_url,
                callback=self.discover_product_urls,
                meta={"keyword": keyword, "page": 1},
            )

    def discover_product_urls(self, response):
        page = response.meta["page"]
        keyword = response.meta["keyword"]

        # Fetching Product URLs
        row = response.css("._75nlfW")
        for i in range(10):
            product = row[i]
            relative_url = product.css("div>a::attr(href)").get().split("&")[0]
            product_url = urljoin("https://www.flipkart.com", relative_url).split("?")[
                0
            ]

            yield scrapy.Request(
                url=product_url,
                callback=self.parse_product_data,
                meta={"keyword": keyword, "page": page},
            )

    def parse_product_data(self, response):
        # Create an item dictionary for product details
        if len(response.css(".pPAw9M a::attr(href)")) > 0:
            product_review_link = response.css(".pPAw9M a::attr(href)")[-1].get()
            product_item = {
                "name": response.css(".VU-ZEz::text").get("").strip(),
                "price": response.css(".CxhGGd::text").get("").strip(),
                "stars": response.css(".XQDdHH::text").get("").strip(),
                "rating_count": response.css(".Wphh3N span::text").get("").strip(),
                "images": response.css(".DByuf4::attr(src)").get(),
                "url": response.url,
            }
            product_item = {k: v for k, v in product_item.items() if v}

            if product_item:
                if product_review_link:
                    product_item["product_review_link"] = product_review_link
                    # Now start scraping reviews for this product
                    flipkart_reviews_url = (
                        f"https://www.flipkart.com{product_review_link}/"
                    )
                    # yield scrapy.Request(
                    #     url=flipkart_reviews_url,
                    #     callback=self.parse_reviews,
                    #     meta={
                    #         "product_review_link": product_review_link,
                    #         "product_item": product_item,
                    #         "retry_count": 0,
                    #     },
                    # )

        # def parse_reviews(self, response):
        #     product_review_link = response.meta["product_review_link"]
        #     product_item = response.meta["product_item"]
        #     retry_count = response.meta["retry_count"]

        #     # Parse Product Reviews
        #     review_elements = response.css(".EPCmJX")
        #     reviews = []
        #     for review_element in review_elements:
        #         reviews.append(
        #             {
        #                 "product_review_link": product_review_link,
        #                 "text": review_element.css("._11pzQk::text").get(),
        #                 "text_2": review_element.css(".ZmyHeo div::text").get(),
        #                 "rating": review_element.css(".XQDdHH::text").get(),
        #             }
        #         )

        # product_item["reviews"] = reviews

        if product_item:
            # Save the product data to JSON file
            self.save_to_json(product_item)

        # Retry logic in case of JS-rendered review pages
        # elif retry_count < 3:
        #     retry_count += 1
        #     yield scrapy.Request(
        #         url=response.url,
        #         callback=self.parse_reviews,
        #         dont_filter=True,
        #         meta={
        #             "product_review_link": product_review_link,
        #             "product_item": product_item,
        #             "retry_count": retry_count,
        #         },
        #     )

    def save_to_json(self, product_item):
        # Append the product data to the specified JSON file
        with open(self.file_name, "a") as json_file:
            json.dump(product_item, json_file, indent=4)
            json_file.write("\n")  # Add a newline for readability between records
