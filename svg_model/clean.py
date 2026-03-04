# svg/clean.py


from svg_model.preBackground import remove_tail_global_like_elements
from svg_model.preTransform import flatten_rotated_rects
def clean_svg_tree(root_elem, svg_root):
    remove_tail_global_like_elements(root_elem,svg_root,max_check=10,area_ratio=0.95,margin_ratio=0.02)
    flatten_rotated_rects(root_elem)






