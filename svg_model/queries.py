
from lxml import etree


def _localname(elem):
    return etree.QName(elem).localname


def find_last(elem, tag: str):
    """
    在 elem 子树中，按文档顺序查找最后一个指定 tag
    """
    last = None
    for e in elem.iter():
        if _localname(e) == tag:
            last = e
    return last
