
def dump_svg_document(doc, *, show_attrs=True, max_attr_len=60):
    if doc is None:
        print("[ERROR] SvgDocument is None")
        return

    print("\n================ SVG DOCUMENT ================\n")

    # ---------- Root ----------
    print("[Root]")
    root = doc.root
    if root:
        vb = getattr(root, "viewbox", None)
        w  = getattr(root, "width", None)
        h  = getattr(root, "height", None)
        print(f"  viewBox : {vb}")
        print(f"  size    : {w} x {h}")
    else:
        print("  (root is None)")

    # ---------- Defs ----------
    print("\n[Defs]")
    defs = doc.defs
    if defs and defs.styles:
        print(f"  styles ({len(defs.styles)})")
        for k, v in defs.styles.items():
            print(f"    {k} -> {v}")
    else:
        print("  (no styles)")

    # ---------- Nodes ----------
    print("\n[Nodes]")
    print(f"  total: {len(doc.nodes)}")

    # 只打印树形结构（parent is None 的作为根）
    roots = [n for n in doc.nodes if n.parent is None]

    def fmt_attrib(attrib):
        if not attrib:
            return ""
        keys = list(attrib.keys())
        s = ", ".join(keys)
        if len(s) > max_attr_len:
            s = s[:max_attr_len] + "..."
        return f" attrs: {s}"

    def walk(node, prefix="", is_last=True):
        branch = "└─" if is_last else "├─"
        line = f"{prefix}{branch}[{node.id}] <{node.tag}> order={node.order}"

        if show_attrs:
            line += fmt_attrib(node.attrib)

        print(line)

        next_prefix = prefix + ("   " if is_last else "│  ")
        count = len(node.children)

        for i, ch in enumerate(node.children):
            walk(ch, next_prefix, i == count - 1)

    for i, root_node in enumerate(roots):
        walk(root_node, "", i == len(roots) - 1)

    print("\n================ END =================\n")