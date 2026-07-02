from pathlib import Path

from scrapy.cmdline import execute


if __name__ == "__main__":
    Path("output").mkdir(exist_ok=True)
    execute(["scrapy", "crawl", "guwendao"])
