from __future__ import annotations

from datetime import datetime
from urllib.parse import urljoin

import scrapy

from poetry_crawler.items import PoetryItem


class GuwendaoSpider(scrapy.Spider):
    name = "guwendao"
    allowed_domains = ["guwendao.net"]
    start_urls = ["https://www.guwendao.net/"]

    custom_settings = {
        "CONCURRENT_REQUESTS": 6,
        "DOWNLOAD_DELAY": 1.2,
    }

    def parse(self, response):
        nav_links = response.css("a::attr(href)").getall()
        for href in nav_links:
            if not href:
                continue
            full_url = urljoin(response.url, href)
            if self._is_list_page(full_url):
                yield scrapy.Request(full_url, callback=self.parse_list)

    def parse_list(self, response):
        detail_links = response.css("a::attr(href)").getall()
        seen = set()
        for href in detail_links:
            if not href:
                continue
            full_url = urljoin(response.url, href)
            if full_url in seen:
                continue
            seen.add(full_url)
            if self._is_detail_page(full_url):
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_detail,
                    meta={
                        "render": True,
                        "wait_selector": "body",
                        "category": self._guess_category(response.url),
                    },
                )

        next_page = response.css("a.next::attr(href), a[title='下一页']::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_list)

    def parse_detail(self, response):
        self.logger.info("进入 parse_detail: %s", response.url)

        item = PoetryItem()
        item["title"] = self._first_match(
            response,
            [
                "h1::text",
                ".title::text",
                ".cont h1::text",
                ".main3 h1::text",
            ],
        )
        item["author"] = self._first_match(
            response,
            [
                ".source a::text",
                ".cont p a::text",
                ".source::text",
            ],
            default="",
        )
        item["dynasty"] = self._extract_dynasty(response)
        item["category"] = response.meta.get("category", "")
        item["tags"] = response.css(".tag a::text, .tags a::text").getall()
        item["content"] = self._extract_joined_text(
            response,
            [
                ".contson::text",
                ".sons .contson *::text",
                ".content *::text",
                ".main3 .contson::text",
            ],
        )
        item["annotation"] = self._extract_section_text(response, ("注释", "注解"))
        item["translation"] = self._extract_section_text(response, ("译文", "翻译"))
        item["appreciation"] = self._extract_section_text(response, ("赏析", "鉴赏"))
        item["background"] = self._extract_section_text(response, ("创作背景", "写作背景"))
        item["source_url"] = response.url
        item["crawl_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if item["title"] and item["content"]:
            yield item
        else:
            self.logger.warning("页面解析结果不完整，请检查选择器: %s", response.url)

    def _is_list_page(self, url: str) -> bool:
        keywords = (
            "/gushi/",
            "/author",
            "/shiwen/",
            "default.aspx",
            "list",
            "/tangshi/",
            "/songci/",
            "/shijing/",
            "/chuci/",
        )
        return any(word in url for word in keywords)

    def _is_detail_page(self, url: str) -> bool:
        keywords = (
            "shiwen_",
            "/mingju/",
            "/shiwen/default_",
            "tangshi_",
            "songci_",
            "shijing_",
            "chuci_",
            ".html",
        )
        return any(word in url for word in keywords)

    def _guess_category(self, url: str) -> str:
        if "tangshi" in url:
            return "唐诗"
        if "songci" in url:
            return "宋词"
        if "shijing" in url:
            return "诗经"
        if "chuci" in url:
            return "楚辞"
        return "古诗文"

    def _extract_dynasty(self, response) -> str:
        text = self._extract_joined_text(
            response,
            [
                ".source::text",
                ".cont p::text",
            ],
        )
        for splitter in ("·", "：", ":"):
            if splitter in text:
                return text.split(splitter)[0].strip()
        return text.strip()

    def _extract_section_text(self, response, keywords) -> str:
        texts = []

        for block in response.css("div, section"):
            joined = "".join(block.css("::text").getall()).strip()
            if not joined:
                continue
            if any(keyword in joined[:20] for keyword in keywords):
                parts = [part.strip() for part in block.css("::text").getall() if part.strip()]
                texts.extend(parts)

        return "\n".join(texts)

    def _extract_joined_text(self, response, selectors) -> str:
        for selector in selectors:
            texts = [text.strip() for text in response.css(selector).getall() if text.strip()]
            if texts:
                return "\n".join(texts)
        return ""

    def _first_match(self, response, selectors, default=None):
        for selector in selectors:
            value = response.css(selector).get()
            if value:
                return value.strip()
        return default
