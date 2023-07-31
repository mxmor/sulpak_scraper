
import os


BOT_NAME = "sulpak_spider"

SPIDER_MODULES = ["sulpak_spider.spiders"]
NEWSPIDER_MODULE = "sulpak_spider.spiders"

ROBOTSTXT_OBEY = False

LOG_LEVEL = 'WARNING'

AUTOTHROTTLE_ENABLED = True

ITEM_PIPELINES = { 'sulpak_spider.pipelines.SulpakSpiderPipeline': 300 }

DOWNLOADER_MIDDLEWARES = {
    'sulpak_spider.middlewares.SulpakSpiderDownloaderMiddleware': 543,
    'sulpak_spider.middlewares.UserAgentMiddleware': 300,
    # 'rotating_proxies.middlewares.RotatingProxyMiddleware': 410,
    # 'rotating_proxies.middlewares.BanDetectionMiddleware': 420,
}

ROTATING_PROXY_LIST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../utils/proxy.txt')



REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"


