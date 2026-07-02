BOT_NAME = "poetry_crawler"

SPIDER_MODULES = ["poetry_crawler.spiders"]
NEWSPIDER_MODULE = "poetry_crawler.spiders"

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True

RETRY_ENABLED = True
RETRY_TIMES = 2
DOWNLOAD_TIMEOUT = 20

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
}

DOWNLOADER_MIDDLEWARES = {
    "poetry_crawler.middlewares.DrissionPageDownloaderMiddleware": 543,
}

ITEM_PIPELINES = {
    "poetry_crawler.pipelines.PoetryPipeline": 300,
}

FEEDS = {
    "output/guwendao_poems.jsonl": {
        "format": "jsonlines",
        "encoding": "utf-8",
        "overwrite": True,
    },
    "output/guwendao_poems.csv": {
        "format": "csv",
        "encoding": "utf-8-sig",
        "overwrite": True,
    },
}

LOG_LEVEL = "INFO"

DRISSION_HEADLESS = True
DRISSION_TIMEOUT = 15

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
