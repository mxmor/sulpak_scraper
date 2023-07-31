import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from dotenv import load_dotenv
import os
from pathlib import Path

levels_up = 2
env_file_path = Path(__file__).parents[levels_up] / ".env"

# Load the environment variables from the .env file.
load_dotenv(dotenv_path=env_file_path)

# Now you can access the environment variable.
sulpak_categories = os.getenv('SULPAK_CATEGORIES').split(',')


class SulpakScraperSpider(CrawlSpider):
    
    name = "sulpak_scraper"
    allowed_domains = ["sulpak.kz"]
    start_urls = sulpak_categories
    # start_urls = ["https://www.sulpak.kz/p/telefoniy_i_gadzhetiy"]

    custom_settings = {
        # 'HTTP_PROXY': 'http://ingp3030607:2iYbbAyXG4@91.227.155.174:7951'
    }

    rules = (
        Rule(LinkExtractor(allow=r'^https://www.sulpak.kz/f/[a-zA-Z0-9_]+$'), follow=False, callback='parse_category'),
    )

    def start_requests(self):
        for url in self.start_urls:
            print(f"Starting category: {url}")
            yield scrapy.Request(url=url, callback=self.parse_category)    

    def parse_category(self, response):
        breadcrumbs = response.css('.mobile-breadcrumb a::text, .mobile-breadcrumb span::text').getall()[1:]
        product_category = f"Сулпак / {' / '.join(breadcrumbs)}"

        products = response.css('div.products__items div.product__item-js')
        for product in products:
            product_sku = int(product.css('::attr(data-code)').get())
            product_title = product.css('::attr(data-name)').get()
            product_price = int(float(product.css('::attr(data-price)').get()))
            product_old_price_selector = product.css('div.product__item-price-old ::text').get()
            product_old_price = int(product_old_price_selector.replace(' ', '').replace('₸', '')) if product_old_price_selector else product_price
            product_url = 'https://www.sulpak.kz' + product.css('div.product__item-images-block a::attr(href)').get()

            item = {
                'sku': product_sku,
                'title': product_title,
                'price': product_price,
                'old_price': product_old_price,
                'url': product_url,
                'category' : product_category,
            }
            yield item




        if response.css('div.pagination'):
        
            if 'page' not in response.url:
                response = response.replace(url=response.url + '?page=1')

            current_page = int(response.url.split('=')[-1])
            last_page = int(response.css('li.pagination__end a::attr(data-url)').get().split('=')[-1])

            if current_page < last_page:
                next_page = current_page + 1
                next_url = response.url.replace(f'page={current_page}', f'page={next_page}')
                yield scrapy.Request(url=next_url, callback=self.parse_category)
