from svg_model.queries import find_last
from svg_model.heuristics import is_global_background_rect

def remove_global_background_rect(root_elem, svg_root):
    last_rect = find_last(root_elem, "rect")
    if last_rect is None:
        return

    if is_global_background_rect(last_rect, svg_root):
        parent = last_rect.getparent()
        if parent is not None:
            parent.remove(last_rect)


