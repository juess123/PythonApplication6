from lxml import etree
from svg_model.model import SvgNode


def build_node_tree(root_elem, doc):

    node_id = 0
    order = 0

    def dfs(elem, parent_node=None):
        nonlocal node_id, order

        tag = etree.QName(elem).localname
        node = SvgNode(node_id, tag, dict(elem.attrib))
        node_id += 1

        node.parent = parent_node
        if parent_node:
            parent_node.children.append(node)

        node.order = order
        order += 1

        doc.nodes.append(node)

        for child in elem:
            dfs(child, node)


    for child in root_elem:
        dfs(child, None)
