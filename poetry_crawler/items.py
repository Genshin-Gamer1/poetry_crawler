import scrapy


class PoetryItem(scrapy.Item):
    title = scrapy.Field()
    dynasty = scrapy.Field()
    author = scrapy.Field()
    category = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()
    annotation = scrapy.Field()
    translation = scrapy.Field()
    appreciation = scrapy.Field()
    background = scrapy.Field()
    source_url = scrapy.Field()
    crawl_time = scrapy.Field()
