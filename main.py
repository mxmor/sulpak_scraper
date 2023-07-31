import schedule
import time
import subprocess
import os
import sys
# from sulpak_spider.utils.category_scraper import scrape_categories


def job():
    scrapy_path = os.path.join(os.path.dirname(sys.executable), 'scrapy')
    subprocess.run([scrapy_path, "crawl", "sulpak_scraper"], cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sulpak_spider'))


def main():
    # scrape_categories()

    job()

    schedule.every(5).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()