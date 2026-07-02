import re


def clean_text(value):
    if value is None:
        return ""
    if isinstance(value, list):
        value = "\n".join(part for part in value if part)
    text = str(value)
    text = re.sub(r"\r", "\n", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t\f\v]+", " ", text)
    return text.strip()


def dedupe_lines(text: str) -> str:
    if not text:
        return ""
    seen = set()
    result = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line in seen:
            continue
        seen.add(line)
        result.append(line)
    return "\n".join(result)
