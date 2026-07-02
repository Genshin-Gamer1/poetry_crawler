from __future__ import annotations

from typing import Optional

from scrapy import signals
from scrapy.http import HtmlResponse

try:
    from DrissionPage import ChromiumOptions, ChromiumPage
except ImportError:  # pragma: no cover
    ChromiumOptions = None
    ChromiumPage = None


class DrissionPageDownloaderMiddleware:
    """对标记了 render=True 的请求执行浏览器渲染。"""

    def __init__(self, timeout: int = 15, headless: bool = True):
        self.timeout = timeout
        self.headless = headless
        self.page: Optional[ChromiumPage] = None

    @classmethod
    def from_crawler(cls, crawler):
        timeout = crawler.settings.getint("DRISSION_TIMEOUT", 15)
        headless = crawler.settings.getbool("DRISSION_HEADLESS", True)
        middleware = cls(timeout=timeout, headless=headless)
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def spider_opened(self, spider):
        if ChromiumPage is None or ChromiumOptions is None:
            spider.logger.warning("DrissionPage 未安装，动态渲染功能不可用。")
            return

        options = ChromiumOptions()
        if self.headless:
            options.headless(True)
        self.page = ChromiumPage(addr_or_opts=options)
        spider.logger.info("DrissionPage 浏览器实例已初始化。")

    def spider_closed(self, spider):
        if self.page:
            self.page.quit()
            spider.logger.info("DrissionPage 浏览器实例已关闭。")

    def process_request(self, request, spider):
        if not request.meta.get("render"):
            return None

        if self.page is None:
            spider.logger.warning("动态页面请求已跳过，原因是浏览器实例不可用: %s", request.url)
            return None

        spider.logger.info("使用 DrissionPage 渲染页面: %s", request.url)
        self.page.get(request.url, timeout=self.timeout)

        wait_selector = request.meta.get("wait_selector")
        if wait_selector:
            try:
                self.page.wait.ele_displayed(wait_selector, timeout=self.timeout)
            except Exception:
                spider.logger.warning("等待元素超时，继续解析当前页面: %s", request.url)

        html = self.page.html
        return HtmlResponse(
            url=request.url,
            body=html.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )
