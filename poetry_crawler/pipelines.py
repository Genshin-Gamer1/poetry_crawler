from __future__ import annotations

from itemadapter import ItemAdapter

from .utils.cleaners import clean_text, dedupe_lines


class PoetryPipeline:
    """统一清洗字段，保证输出结构整洁。"""

    text_fields = (
        "title",
        "dynasty",
        "author",
        "category",
        "content",
        "annotation",
        "translation",
        "appreciation",
        "background",
    )

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        for field in self.text_fields:
            adapter[field] = clean_text(adapter.get(field))

        adapter["content"] = dedupe_lines(adapter.get("content"))
        adapter["annotation"] = dedupe_lines(adapter.get("annotation"))
        adapter["translation"] = dedupe_lines(adapter.get("translation"))
        adapter["appreciation"] = dedupe_lines(adapter.get("appreciation"))
        adapter["background"] = dedupe_lines(adapter.get("background"))

        tags = adapter.get("tags") or []
        adapter["tags"] = [clean_text(tag) for tag in tags if clean_text(tag)]
        return item
