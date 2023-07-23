import schedule
import time
import subprocess
import os
from sulpak_spider.utils.category_scraper import scrape_categories


# scrape_categories()

def job():
    subprocess.run(["scrapy", "crawl", "sulpak_scraper", "-o", "products.csv"], cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sulpak_spider'))

job()

schedule.every(10).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)