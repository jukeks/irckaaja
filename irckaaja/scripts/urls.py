import re
from typing import Any, List


def parse_urls(string: str) -> List[Any]:
    return re.findall(r"(https?://\S+)", string)
