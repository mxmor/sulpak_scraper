# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import psycopg2
import os
from datetime import datetime, timedelta
from math import ceil

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
import asyncio
import urllib

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))


class SulpakSpiderPipeline:
    def __init__(self):
        self.bot = Bot(token=os.getenv('SULPAK_TELEGRAM_API_TOKEN'))
        self.telegram_channel_id = os.getenv('SULPAK_TELEGRAM_CHANNEL_ID')

    def open_spider(self, spider):
        hostname = 'localhost'
        username = 'postgres'
        password = os.getenv('SULPAK_DATABASE_PASSWORD')
        database = 'sulpak'
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

    async def process_item(self, item, spider):
        sku = item.get('sku')
        price = item.get('price')
        old_price = item.get('old_price')
        url = item.get('url')
        title = item.get('title')
        category = item.get('category')

        self.cursor.execute("SELECT COUNT(*) FROM products WHERE sku = %s", (sku,))
        product_exists = self.cursor.fetchone()[0] > 0

        if not product_exists:
            product_record = (sku, title, category, url)
            self.cursor.execute("""
                INSERT INTO products (sku, title, category, url) 
                VALUES(%s, %s, %s, %s)
            """, product_record)

            last_price_change = 0
            price_record = (sku, datetime.now(), old_price, last_price_change)
            self.cursor.execute("""
                INSERT INTO prices (sku, parse_date, price, price_change) 
                VALUES(%s, %s, %s, %s)
            """, price_record)

            price_change = int(((ceil(price / old_price * 100)) / 100 - 1) * 100)

            if price_change < 0:
                price_record = (sku, datetime.now() + timedelta(seconds=1), price, price_change)
                self.cursor.execute("""
                    INSERT INTO prices (sku, parse_date, price, price_change) 
                    VALUES(%s, %s, %s, %s)
                """, price_record)

        else:
            self.cursor.execute("SELECT price FROM prices WHERE sku = %s ORDER BY parse_date DESC LIMIT 1", (sku,))
            last_price = self.cursor.fetchone()[0]
            price_change = int(((ceil(price / last_price * 100)) / 100 - 1) * 100)

            if price_change != 0:
                price_record = (sku, datetime.now(), price, price_change)
                self.cursor.execute("""
                    INSERT INTO prices (sku, parse_date, price, price_change) 
                    VALUES(%s, %s, %s, %s)
                """, price_record)

            self.cursor.execute("SELECT price_change FROM prices WHERE sku = %s ORDER BY parse_date DESC LIMIT 1", (sku,))
            last_price_change = self.cursor.fetchone()[0]

        if price_change < -50 and price_change != last_price_change:
            message = f"<b>{title}</b>\n{category}\n\n"
            self.cursor.execute("SELECT parse_date, price, price_change FROM prices WHERE sku = %s ORDER BY parse_date DESC LIMIT 6", (sku,))
            price_history = self.cursor.fetchall()
            for price_record in price_history:
                parse_date, price, price_change = price_record
                message += f"{parse_date.strftime('%d.%m.%Y')}: {'{:,}'.format(price).replace(',', ' ')} \N{TENGE SIGN} ({price_change}%)\n"
            message += f"\n{url}"


            query = urllib.parse.quote_plus(title)
            google_url = f"https://google.com/search?q={query}"
            yandex_url = f"https://market.yandex.kz/search?text={query}"
            kaspi_url = f"https://kaspi.kz/shop/search/?text={query}"
            google_button = InlineKeyboardButton(text="Google", url=google_url)
            yandex_button = InlineKeyboardButton(text="Yandex", url=yandex_url)
            kaspi_button = InlineKeyboardButton(text="Kaspi", url=kaspi_url)
            keyboard = InlineKeyboardMarkup([[yandex_button, kaspi_button, google_button]])
            await self.bot.send_message(chat_id=self.telegram_channel_id, text=message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            await asyncio.sleep(3)


        self.connection.commit()
        return item 
