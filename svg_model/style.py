import re
from lxml import etree

STYLE_BLOCK_RE = re.compile(
    r"\.([a-zA-Z0-9_-]+)\s*\{([^}]*)\}",
    re.S,
)

DECL_RE = re.compile(
    r"([a-zA-Z-]+)\s*:\s*([^;]+)"
)
def extract_style_defs(root_elem):

    styles = {}

 
    for elem in root_elem.iter():
        tag = etree.QName(elem).localname
        if tag != "style":
            continue

        if not elem.text:
            continue

        css_text = elem.text

  
        for cls_name, body in STYLE_BLOCK_RE.findall(css_text):
            props = {}

            for key, val in DECL_RE.findall(body):
                props[key.strip()] = val.strip()

            if props:
                styles[cls_name] = props

    return styles



_CLIP_RE = re.compile(r"clip-path\s*:\s*url\(#([^)]+)\)")

def parse_clip_id_from_style(style: str | None) -> str | None:
    """
    从 style 字符串中提取 clip-path 的 id
    返回：
      - "id2"
      - None
    """
    if not style:
        return None

    m = _CLIP_RE.search(style)
    if not m:
        return None

    return m.group(1)
