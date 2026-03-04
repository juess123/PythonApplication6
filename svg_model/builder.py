from lxml import etree
from svg_model.model import SvgDocument, SvgRoot, SvgDefs
from svg_model.geometry import init_svg_root_geometry
from svg_model.style import extract_style_defs
from svg_model.preprocess import remove_global_background_rect
from svg_model.tree import build_node_tree
from svg_model.clean import clean_svg_tree

def build_svg_document(svg_file: str) -> SvgDocument:
    parser = etree.XMLParser(huge_tree=True)
    tree = etree.parse(svg_file, parser)
    root_elem = tree.getroot()

    doc = SvgDocument()

    # -------- 1. 解析 SvgRoot --------
    doc.root = SvgRoot(raw_attrib=root_elem.attrib)
    init_svg_root_geometry(root_elem, doc.root)

    # -------- 2. 预处理（XML 清洗 / 规则）--------
    clean_svg_tree(root_elem, doc.root)

    # -------- 3. defs / styles --------
    doc.defs = SvgDefs()
    doc.defs.styles = extract_style_defs(root_elem)

    # -------- 4. 构建 SvgNode 树 --------
    build_node_tree(root_elem, doc)

    return doc
def get_svg_size_mm(svg_file: str) -> tuple[float, float]:
    """
    直接从 SVG 文件获取宽高（单位：mm）

    Returns:
        (width_mm, height_mm)
    """
    doc = build_svg_document(svg_file)
    return doc.root.width_mm, doc.root.height_mm