# -*- coding: utf-8 -*-
# created at: 2022/9/20 23:18
# author    : Gao Kai
# Email     : gaosimin1@163.com


import os.path
from PIL import Image, ImageFont, ImageDraw, ImageFilter


NULL_FONT = ImageFont.truetype("interface\\font\\bahnschrift.ttf", size=24, index=0)
NULL_FONT.set_variation_by_name("Bold SemiCondensed")

NODE_NAME_FONT = ImageFont.truetype("interface\\font\\bahnschrift.ttf", size=16, index=0)
NODE_NAME_FONT.set_variation_by_name("SemiCondensed")

NODE_TITLE_FONT = ImageFont.truetype("interface\\font\\bahnschrift.ttf", size=18, index=0)
NODE_TITLE_FONT.set_variation_by_name("Bold SemiCondensed")

PLACE_HOLDER_NAME_FONT = ImageFont.truetype("interface\\font\\bahnschrift.ttf", size=48, index=0)
PLACE_HOLDER_NAME_FONT.set_variation_by_name("Condensed")

PLACE_HOLDER_CONTENT_FONT = ImageFont.truetype("interface\\font\\bahnschrift.ttf", size=14, index=0)
PLACE_HOLDER_CONTENT_FONT.set_variation_by_name("Bold Condensed")

OUT_LINK_FONT = ImageFont.truetype("interface\\font\\bahnschrift.ttf", size=18, index=0)
OUT_LINK_FONT.set_variation_by_name("Bold Condensed")

GRID_SIZE = 40
SMALL_GLOW_GRID_SIZE = int(2 * GRID_SIZE)
LARGE_GLOW_GRID_SIZE = int(4 * GRID_SIZE)


EDITOR_NOT_HOVERED = 0
EDITOR_HOVERED = 1
EDITOR_NODE_NAME_HOVERED = 2
EDITOR_PH_HOVERED = 3
EDITOR_OUT_LINK_HOVERED = 4


SPACING_CONSTANT = {
    0: (0, 0),
    1: (0, 0),
    2: (85, 10),
    3: (55, 5)
}

FSA_SPACING_CONSTANT = {
    0: (),
    1: (4, 0),
    2: (1.875, 0.25),
    3: (1.25, 0.125)
}


TURNER_KEYWORD = {
    "nw": "tl",
    "ne": "tr",
    "sw": "dl",
    "se": "dr",
    "wn": "dr",
    "en": "dl",
    "ws": "tr",
    "es": "tl"
}


def draw_fsa_deselected_display(width, height):
    if height > 0 and width > 0:
        _res = Image.new("RGBA", (width, height), color=(20, 0, 90, 255))

        _d = ImageDraw.Draw(_res)
        _d.text((round(width/2), round(height/2)),
                "No FSA Selected", fill=(255, 255, 255, 128), anchor='mm', font=NULL_FONT)

        return _res
    else:
        return None


def draw_background_display(width, height, _x, _y, _c):
    if _c:
        _c1 = (90, 0, 20, 255)
        _c2 = (120, 70, 90, 255)
    else:
        _c1 = (20, 0, 90, 255)
        _c2 = (70, 90, 120, 255)

    if height > 0 and width > 0:
        _res = Image.new("RGBA", (width, height), color=_c1)

        _d = ImageDraw.Draw(_res)

        # lets set GRID_SIZE as a unit
        offset_x = round(width / 2 - _x * GRID_SIZE) % GRID_SIZE
        offset_y = round(height / 2 + _y * GRID_SIZE) % GRID_SIZE
        line_horizontals = [offset_x+_i*GRID_SIZE for _i in range(0, (width-offset_x)//GRID_SIZE+1)]
        line_verticals = [offset_y+_i*GRID_SIZE for _i in range(0, (height-offset_y)//GRID_SIZE+1)]

        for _line in line_horizontals:
            _d.line([_line, 0, _line, height], fill=_c2)

        for _line in line_verticals:
            _d.line([0, _line, width, _line], fill=_c2)

        return _res
    else:
        return None


def load_node_icon(icon_folder_path, _node_class_dict):
    _node_image_pool = dict()

    _default_path = os.path.join(icon_folder_path, "Default.png")
    with Image.open(_default_path) as _raw_icon:
        _raw_icon.load()

    _default_icon_mask = Image.new("RGBA", (_raw_icon.width, _raw_icon.height), color=(255, 255, 255, 100))

    _default_icon_mask2 = Image.new("RGBA", (_raw_icon.width, _raw_icon.height), color=(255, 255, 255, 0))
    _default_icon_mask2.paste(_default_icon_mask, mask=_raw_icon.getchannel("A"))

    _default_icon_mask3 = Image.new("RGBA", (_raw_icon.width, _raw_icon.height), color=(255, 255, 255, 0))
    _default_icon_mask3.paste(Image.new("RGBA", (_raw_icon.width, _raw_icon.height), color=(255, 255, 255, 255)),
                              mask=_raw_icon.getchannel("A"))
    _default_out_glow = small_out_glow_gen(_default_icon_mask3, 4)
    _default_out_glow2 = small_out_glow_gen(_default_icon_mask3, 12)

    _default_icon_mask4 = Image.new("RGBA", (_raw_icon.width, _raw_icon.height), color=(255, 255, 255, 0))
    _default_icon_mask4.paste(Image.new("RGBA", (_raw_icon.width, _raw_icon.height), color=(20, 0, 90, 200)),
                              mask=_raw_icon.getchannel("A"))

    for node_class_name in _node_class_dict:
        icon_path = os.path.join(icon_folder_path, node_class_name + ".png")
        if not os.path.isfile(icon_path):
            icon_path = _default_path

        with Image.open(icon_path) as _raw_icon:
            _raw_icon.load()

        _raw_icon_mask = _default_icon_mask2.copy()
        _raw_icon_fade = _default_icon_mask4.copy()

        # hovered
        _raw_icon_masked = Image.alpha_composite(_raw_icon, _raw_icon_mask)

        # faded
        _raw_icon_faded = Image.alpha_composite(_raw_icon, _raw_icon_fade)

        # selected
        _raw_icon_out_glowing = _default_out_glow.copy()
        _raw_icon_out_glowing.paste(_raw_icon, (64, 64), mask=_raw_icon.getchannel("A"))

        # selected and hovered
        _raw_icon_out_glowing_masked = _default_out_glow.copy()
        _raw_icon_out_glowing_masked.paste(_raw_icon_masked, (64, 64), mask=_raw_icon.getchannel("A"))

        # running
        _raw_icon_out_glowing2 = _default_out_glow2.copy()
        _raw_icon_out_glowing2.paste(_raw_icon, (192, 192), mask=_raw_icon.getchannel("A"))

        _icon = _raw_icon.resize((GRID_SIZE, GRID_SIZE))
        _icon_hovered = _raw_icon_masked.resize((GRID_SIZE, GRID_SIZE))
        _icon_faded = _raw_icon_faded.resize((GRID_SIZE, GRID_SIZE))
        _icon_selected = _raw_icon_out_glowing.resize((SMALL_GLOW_GRID_SIZE, SMALL_GLOW_GRID_SIZE))
        _icon_hovered_selected = _raw_icon_out_glowing_masked.resize((SMALL_GLOW_GRID_SIZE, SMALL_GLOW_GRID_SIZE))
        _icon_running = _raw_icon_out_glowing2.resize((SMALL_GLOW_GRID_SIZE, SMALL_GLOW_GRID_SIZE))

        _node_image_pool[node_class_name] = (_icon, _icon_hovered, _icon_selected,
                                             _icon_hovered_selected, _icon_faded, _icon_running)

    return _node_image_pool


def load_var_icon(icon_folder_path, _var_class_dict):
    var_icon_pool = dict()

    for var_class_name in _var_class_dict:
        icon_path = os.path.join(icon_folder_path, var_class_name + ".png")

        with Image.open(icon_path) as _raw_icon:
            _raw_icon.load()
        var_icon_pool[var_class_name] = _raw_icon.resize((64, 64))

    return var_icon_pool


def small_out_glow_gen(_img, radius) -> Image:
    _out_glow = Image.new("RGBA", (_img.width+32*radius, _img.height+32*radius), color=(255, 255, 255, 0))
    _out_glow.paste(_img, (16*radius, 16*radius), mask=_img)
    _out_glow = _out_glow.filter(ImageFilter.GaussianBlur(radius=radius*7))
    return Image.alpha_composite(_out_glow, _out_glow)


def large_out_glow_gen(_img, radius) -> Image:
    _out_glow = Image.new("RGBA", (_img.width+32*radius, _img.height+32*radius), color=(255, 255, 255, 0))
    _out_glow.paste(_img, (16*radius, 16*radius), mask=_img)
    _out_glow = _out_glow.filter(ImageFilter.GaussianBlur(radius=radius*3))
    _out_glow = Image.alpha_composite(_out_glow, _out_glow)
    return Image.alpha_composite(_out_glow, _out_glow)


def put_image_by_xy(_dest: Image, _x, _y, _img: Image):
    _dest = _dest.copy()
    _dest.alpha_composite(_img, dest=(_x, _y-_img.height))
    return _dest


def generate_node_buffer(_node_name, _node_content):
    _node_buffer = dict()

    _node_buffer["x"] = _node_content["x"]
    _node_buffer["y"] = _node_content["y"]
    _node_buffer["type"] = _node_content["type"]

    _node_buffer["show-name"] = True   # change this to _node_content["show-name"] later

    # name painter
    _l = int(NODE_NAME_FONT.getlength(_node_name))+1

    text_painted = Image.new("RGBA", (_l, 26), color=(0, 0, 0, 0))
    _d = ImageDraw.Draw(text_painted)
    _d.text((0, 0), _node_name, fill=(255, 255, 255, 255), font=NODE_NAME_FONT)

    text_painted_hovered = Image.new("RGBA", (_l, 26), color=(0, 0, 0, 0))
    _d = ImageDraw.Draw(text_painted_hovered)
    _d.text((0, 0), _node_name, fill=(255, 255, 150, 255), font=NODE_NAME_FONT)

    _node_buffer["name"] = text_painted
    _node_buffer["h-name"] = text_painted_hovered

    return _node_buffer


def composite_2_layers(layer_1, layer_2):
    if layer_2:
        return Image.alpha_composite(layer_1, layer_2)
    else:
        return layer_1


def draw_node_layer(_w, _h, node_buffer: dict, hovered_node, selected_nodes, node_image_pool, selected_ghost=False):

    _layer = Image.new("RGBA", (_w, _h), color=(0, 0, 0, 0))
    for node_name, node in node_buffer.items():
        _selected = node_name in selected_nodes
        _hovered = node_name == hovered_node
        if _selected:
            if selected_ghost:
                _layer.alpha_composite(node_image_pool[node["type"]][4], dest=(node["px"], node["py"]-GRID_SIZE))
            elif _hovered:
                _layer.alpha_composite(node_image_pool[node["type"]][3], dest=(node["px"]-20, node["py"]-20-GRID_SIZE))
            else:
                _layer.alpha_composite(node_image_pool[node["type"]][2], dest=(node["px"]-20, node["py"]-20-GRID_SIZE))
        else:
            if _hovered:
                _layer.alpha_composite(node_image_pool[node["type"]][1], dest=(node["px"], node["py"]-GRID_SIZE))
            else:
                _layer.alpha_composite(node_image_pool[node["type"]][0], dest=(node["px"], node["py"]-GRID_SIZE))
        if not (_selected and selected_ghost):
            if node["show-name"]:
                if _hovered:
                    _layer.alpha_composite(node["h-name"], dest=(node["px"] + 60, node["py"] - 28))
                else:
                    _layer.alpha_composite(node["name"], dest=(node["px"] + 60, node["py"] - 28))
    return _layer


def add_selection_bbox(_img, x1, y1, x2, y2):
    selection_box_img = Image.new("RGBA", (_img.width, _img.height), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(selection_box_img)
    _d.rectangle([x1, y1, x2, y2], fill=(150, 120, 210, 100), outline=(255, 255, 255, 200))
    return Image.alpha_composite(_img, selection_box_img)


def draw_node_editor_general_parts(_node_class_dict: dict, _var_image_pool: dict, _node_editor_stitches: dict):

    _node_editor_frame_pool = dict()

    for _node, _node_class in _node_class_dict.items():
        # calculate the height needed. width is a constant, which is 128*4 and occupies LARGE_GLOW_GRID_SIZE
        _n_var = len(_node_class.template_dict["var"])
        _height = 192 + _n_var * 144
        _width = 512
        _resize_height = _height // 16 * 5

        _editor_frame = Image.new("RGBA", (_width, _height), color=(255, 255, 255, 0))

        _d = ImageDraw.Draw(_editor_frame)
        _d.rounded_rectangle([0, 0, _width, _height-96], radius=42, fill=(21, 0, 63, 255), outline=(255, 255, 255, 255), width=7)

        # test the title
        # _d.text((64, 20), "Eval1", fill=(255, 255, 255, 255), font=NODE_TITLE_FONT)

        # _d.line([0, 193, _width, 193], fill=(255, 0, 0, 255), width=1)
        if _node_class.template_dict["var"]:
            _d.line([0, 91, _width, 91], fill=(255, 255, 255, 255), width=10)

        counter = 0
        ph_fillers = dict()
        for _ph_name, _ph_dict in _node_class.template_dict["var"].items():
            _d.text((96, counter*144+109), _ph_name, fill=(255, 255, 255, 255), font=PLACE_HOLDER_NAME_FONT)
            _editor_frame.alpha_composite(_var_image_pool[_ph_dict["type"]], dest=(16, counter*144+104))
            counter += 1

            # _d.rectangle((96, counter*144+256, 480, counter*144+304), fill=(255, 255, 255, 255), outline=(255, 255, 255, 255), width=2)
            # _d.text((112, counter*144+256), _ph_name, fill=(21, 0, 63, 255), font=PLACE_HOLDER_CONTENT_FONT)

            ph_fillers[_ph_name] = (
                _node_editor_stitches["ph-box"][0].copy(), _node_editor_stitches["ph-box"][1].copy(),
                _node_editor_stitches["ph-box"][2].copy(), _node_editor_stitches["ph-box"][3].copy()
            )

        if len(_node_class.template_dict["out-link"]) == 1:
            _stitch_kwd = "large-link"
            _stitch_middle = (80, 14)
        elif len(_node_class.template_dict["out-link"]) == 2:
            _stitch_kwd = "middle-link"
            _stitch_middle = (37, 14)
        else:
            _stitch_kwd = "small-link"
            _stitch_middle = (25, 14)

        _output_stitches = dict()
        _index_count = 1
        for _output in _node_class.template_dict["out-link"].keys():
            _s1 = _node_editor_stitches[_stitch_kwd][0].copy()
            _d = ImageDraw.Draw(_s1)
            _d.text(_stitch_middle, f"{_index_count}. {_output}", fill=(255, 255, 255, 255), font=OUT_LINK_FONT, anchor="mm")

            _s2 = _node_editor_stitches[_stitch_kwd][1].copy()
            _d = ImageDraw.Draw(_s2)
            _d.text(_stitch_middle, f"{_index_count}. {_output}", fill=(255, 255, 150, 255), font=OUT_LINK_FONT, anchor="mm")

            _s3 = _node_editor_stitches[_stitch_kwd][2].copy()
            _d = ImageDraw.Draw(_s3)
            _d.text(_stitch_middle, f"{_index_count}. {_output}", fill=(21, 0, 63, 255), font=OUT_LINK_FONT, anchor="mm")

            _s4 = _node_editor_stitches[_stitch_kwd][3].copy()
            _d = ImageDraw.Draw(_s4)
            _d.text(_stitch_middle, f"{_index_count}. {_output}", fill=(21, 0, 63, 255), font=OUT_LINK_FONT, anchor="mm")

            _output_stitches[_output] = (_s1, _s2, _s3, _s4)
            _index_count += 1

        _node_editor_frame_pool[_node] = (_editor_frame.resize((160, _resize_height)), ph_fillers, _output_stitches)

    return _node_editor_frame_pool


def draw_link_stitches():
    line_width = 9
    line_part_length = 640
    turner_radius = 20
    turner_part_width = 82
    half_line_width = line_width//2
    turner_real_r = turner_radius*2+line_width//2

    # 4 arrows
    _arrow_img = Image.new("RGBA", (32, 48))
    _d = ImageDraw.Draw(_arrow_img)
    _d.line((16, 0, 16, 15), fill=(255, 255, 255, 255), width=line_width)
    _d.polygon((3, 0, 16, 6, 29, 0, 16, 45), fill=(255, 255, 255, 255), outline=(255, 255, 255, 255), width=1)

    _arrow_hovered_img = Image.new("RGBA", (32, 48))
    _d = ImageDraw.Draw(_arrow_hovered_img)
    _d.line((16, 0, 16, 15), fill=(255, 255, 150, 255), width=line_width)
    _d.polygon((3, 0, 16, 6, 29, 0, 16, 45), fill=(255, 255, 150, 255), outline=(255, 255, 150, 255), width=1)

    _arrow_n = (_arrow_img.resize((11, 16)), _arrow_hovered_img.resize((11, 16)))
    _arrow_e = (_arrow_n[0].transpose(Image.Transpose.ROTATE_90), _arrow_n[1].transpose(Image.Transpose.ROTATE_90))
    _arrow_s = (_arrow_n[0].transpose(Image.Transpose.ROTATE_180), _arrow_n[1].transpose(Image.Transpose.ROTATE_180))
    _arrow_w = (_arrow_n[0].transpose(Image.Transpose.ROTATE_270), _arrow_n[1].transpose(Image.Transpose.ROTATE_270))

    _arrow = {
        "s": _arrow_s, "e": _arrow_e, "n": _arrow_n, "w": _arrow_w
    }

    # 4 turners
    _turner_img = Image.new("RGBA", (turner_part_width, turner_part_width))
    _d = ImageDraw.Draw(_turner_img)
    _d.line((40, 0, 40, 20), fill=(255, 255, 255, 255), width=line_width+1)
    _d.line((0, 40, 20, 40), fill=(255, 255, 255, 255), width=line_width+1)
    _d.arc((-half_line_width, -half_line_width, turner_real_r, turner_real_r), 0, 90, fill=(255, 255, 255, 255), width=line_width+1)

    _turner_hovered_img = Image.new("RGBA", (turner_part_width, turner_part_width))
    _d = ImageDraw.Draw(_turner_hovered_img)
    _d.line((40, 0, 40, 20), fill=(255, 255, 150, 255), width=line_width)
    _d.line((0, 40, 20, 40), fill=(255, 255, 150, 255), width=line_width)
    _d.arc((-half_line_width, -half_line_width, turner_real_r, turner_real_r), 0, 90, fill=(255, 255, 150, 255), width=line_width)

    _tl_turner = (_turner_img.resize((25, 25)), _turner_hovered_img.resize((25, 25)))
    _dl_turner = (_tl_turner[0].transpose(Image.Transpose.ROTATE_90), _tl_turner[1].transpose(Image.Transpose.ROTATE_90))
    _dr_turner = (_tl_turner[0].transpose(Image.Transpose.ROTATE_180), _tl_turner[1].transpose(Image.Transpose.ROTATE_180))
    _tr_turner = (_tl_turner[0].transpose(Image.Transpose.ROTATE_270), _tl_turner[1].transpose(Image.Transpose.ROTATE_270))

    _turner = {
        "tl": _tl_turner, "dl": _dl_turner, "dr": _dr_turner, "tr": _tr_turner
    }

    # 2 directions
    _line_img = Image.new("RGBA", (line_part_length, 15))
    _d = ImageDraw.Draw(_line_img)
    _d.line((0, 7, line_part_length, 7), fill=(255, 255, 255, 255), width=line_width)

    _hovered_line_img = Image.new("RGBA", (line_part_length, 15))
    _d = ImageDraw.Draw(_hovered_line_img)
    _d.line((0, 7, line_part_length, 7), fill=(255, 255, 150, 255), width=line_width)

    _horizontal_line = _line_img.copy()
    _horizontal_hovered_line = _hovered_line_img.copy()

    _hor = (_horizontal_line.resize((200, 5)), _horizontal_hovered_line.resize((200, 5)))

    _vertical_line = _line_img.transpose(Image.Transpose.TRANSVERSE)
    _vertical_hovered_line = _hovered_line_img.transpose(Image.Transpose.TRANSVERSE)

    _ver = (_vertical_line.resize((5, 200)), _vertical_hovered_line.resize((5, 200)))

    _line = {
        "h": _hor, "v": _ver
    }

    return _line, _turner, _arrow


def draw_node_editor_stitches():
    _stitches = dict()

    # place holder box
    _ph_nh_ns = Image.new("RGBA", (384, 48), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_ph_nh_ns)
    _d.rectangle((0, 0, 384, 48), fill=(21, 0, 63, 255), outline=(255, 255, 255, 255), width=6)

    _ph_h_ns = Image.new("RGBA", (384, 48), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_ph_h_ns)
    _d.rectangle((0, 0, 384, 48), fill=(21, 0, 63, 255), outline=(255, 255, 150, 255), width=6)

    _ph_nh_s = Image.new("RGBA", (384, 48), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_ph_nh_s)
    _d.rectangle((0, 0, 384, 48), fill=(255, 255, 255, 255), outline=(255, 255, 255, 255), width=6)

    _ph_h_s = Image.new("RGBA", (384, 48), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_ph_h_s)
    _d.rectangle((0, 0, 384, 48), fill=(255, 255, 150, 255), outline=(255, 255, 150, 255), width=6)

    _stitches["ph-box"] = (_ph_nh_ns.resize((120, 15)), _ph_h_ns.resize((120, 15)),
                           _ph_nh_s.resize((120, 15)), _ph_h_s.resize((120, 15)))

    # link boxes (of different size)
    _large_link_nh_ns = Image.new("RGBA", (512, 80), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_large_link_nh_ns)
    _d.rounded_rectangle([0, 0, 512, 80], radius=32, fill=(21, 0, 63, 255), outline=(255, 255, 255, 255), width=7)

    _large_link_h_ns = Image.new("RGBA", (512, 80), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_large_link_h_ns)
    _d.rounded_rectangle([0, 0, 512, 80], radius=32, fill=(21, 0, 63, 255), outline=(255, 255, 150, 255), width=7)

    _large_link_nh_s = Image.new("RGBA", (512, 80), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_large_link_nh_s)
    _d.rounded_rectangle([0, 0, 512, 80], radius=32, fill=(255, 255, 255, 255), outline=(255, 255, 255, 255), width=7)

    _large_link_h_s = Image.new("RGBA", (512, 80), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_large_link_h_s)
    _d.rounded_rectangle([0, 0, 512, 80], radius=32, fill=(255, 255, 150, 255), outline=(255, 255, 150, 255), width=7)

    _stitches["large-link"] = (_large_link_nh_ns.resize((160, 25)), _large_link_h_ns.resize((160, 25)),
                               _large_link_nh_s.resize((160, 25)), _large_link_h_s.resize((160, 25)))

    _middle_link_nh_ns = Image.new("RGBA", (240, 80), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_middle_link_nh_ns)
    _d.rounded_rectangle([0, 0, 240, 80], radius=32, fill=(21, 0, 63, 255), outline=(255, 255, 255, 255), width=7)

    _middle_link_h_ns = Image.new("RGBA", (240, 80), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_middle_link_h_ns)
    _d.rounded_rectangle([0, 0, 240, 80], radius=32, fill=(21, 0, 63, 255), outline=(255, 255, 150, 255), width=7)

    _middle_link_nh_s = Image.new("RGBA", (240, 80), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_middle_link_nh_s)
    _d.rounded_rectangle([0, 0, 240, 80], radius=32, fill=(255, 255, 255, 255), outline=(255, 255, 255, 255), width=7)

    _middle_link_h_s = Image.new("RGBA", (240, 80), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_middle_link_h_s)
    _d.rounded_rectangle([0, 0, 240, 80], radius=32, fill=(255, 255, 150, 255), outline=(255, 255, 150, 255), width=7)

    _stitches["middle-link"] = (_middle_link_nh_ns.resize((75, 25)), _middle_link_h_ns.resize((75, 25)),
                                _middle_link_nh_s.resize((75, 25)), _middle_link_h_s.resize((75, 25)))

    _small_link_nh_ns = Image.new("RGBA", (160, 80), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_small_link_nh_ns)
    _d.rounded_rectangle([0, 0, 160, 80], radius=32, fill=(21, 0, 63, 255), outline=(255, 255, 255, 255), width=7)

    _small_link_h_ns = Image.new("RGBA", (160, 80), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_small_link_h_ns)
    _d.rounded_rectangle([0, 0, 160, 80], radius=32, fill=(21, 0, 63, 255), outline=(255, 255, 150, 255), width=7)

    _small_link_nh_s = Image.new("RGBA", (160, 80), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_small_link_nh_s)
    _d.rounded_rectangle([0, 0, 160, 80], radius=32, fill=(255, 255, 255, 255), outline=(255, 255, 255, 255), width=7)

    _small_link_h_s = Image.new("RGBA", (160, 80), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_small_link_h_s)
    _d.rounded_rectangle([0, 0, 160, 80], radius=32, fill=(255, 255, 150, 255), outline=(255, 255, 150, 255), width=7)

    _stitches["small-link"] = (_small_link_nh_ns.resize((50, 25)), _small_link_h_ns.resize((50, 25)),
                               _small_link_nh_s.resize((50, 25)), _small_link_h_s.resize((50, 25)))

    return _stitches


def draw_note_editor_placeholder(_var_name, _node_editor_stitches: dict):
    if not _var_name:
        _var_name = ""

    if _var_name:
        ph_fillers = (
            _node_editor_stitches["ph-box"][2].copy(), _node_editor_stitches["ph-box"][3].copy()
        )
    else:
        ph_fillers = (
            _node_editor_stitches["ph-box"][0].copy(), _node_editor_stitches["ph-box"][1].copy()
        )

    _d = ImageDraw.Draw(ph_fillers[0])
    _d.text((12, 0), _var_name, fill=(21, 0, 63, 255), font=PLACE_HOLDER_CONTENT_FONT)
    _d = ImageDraw.Draw(ph_fillers[1])
    _d.text((12, 0), _var_name, fill=(21, 0, 63, 255), font=PLACE_HOLDER_CONTENT_FONT)

    return ph_fillers


def draw_note_editor_title(_node_name: str):
    _l = 22
    _w = round(NODE_TITLE_FONT.getlength(_node_name))+1

    _title = Image.new("RGBA", (_w, _l), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_title)
    _d.text((0, 0), _node_name, fill=(255, 255, 255, 255), font=NODE_TITLE_FONT)

    _hovered_title = Image.new("RGBA", (_w, _l), color=(255, 255, 255, 0))
    _d = ImageDraw.Draw(_hovered_title)
    _d.text((0, 0), _node_name, fill=(255, 255, 150, 255), font=NODE_TITLE_FONT)

    return _title, _hovered_title


def update_node_editor_patches(_node_name, _node_content, _node_editor_stitches, _node_editor_pool):
    _editor_title_img = draw_note_editor_title(_node_name)
    _ph_img = dict()
    for _var_name in _node_content["var"]:
        _ph_img[_var_name] = draw_note_editor_placeholder(_node_content["var"][_var_name]["name"], _node_editor_stitches)

    _outs = _node_editor_pool[_node_content["type"]][2]
    _link_cursor = dict()
    for _out_name, _out_content in _outs.items():
        _out_image = _outs[_out_name][0].resize((_outs[_out_name][0].width // 3 * 2, _outs[_out_name][0].height // 3 * 2))
        _link_cursor[_out_name] = Image.new("RGBA", (max(_editor_title_img[0].width, _out_image.width), 50), color=(255, 255, 255, 0))
        _link_cursor[_out_name].alpha_composite(_editor_title_img[0], dest=(1, 13))
        _link_cursor[_out_name].alpha_composite(_out_image, dest=(0, 33))

    return _node_editor_pool[_node_content["type"]][0], _editor_title_img, _ph_img, _node_editor_pool[_node_content["type"]][2], _link_cursor


def draw_node_editor(_node_content, node_editor_patch, hover_state, hover_buffer_content):
    _node_editor_frame = node_editor_patch[0].copy()
    if hover_state == EDITOR_NODE_NAME_HOVERED:
        _node_editor_frame.alpha_composite(node_editor_patch[1][1], (10, 5))
    else:
        _node_editor_frame.alpha_composite(node_editor_patch[1][0], (10, 5))

    if hover_state == EDITOR_PH_HOVERED:
        for _ph_id, _ph in enumerate(_node_content["var"]):
            if _ph == hover_buffer_content:
                _node_editor_frame.alpha_composite(node_editor_patch[2][_ph][1], (30, 50+_ph_id*45))
            else:
                _node_editor_frame.alpha_composite(node_editor_patch[2][_ph][0], (30, 50+_ph_id*45))
    else:
        for _ph_id, _ph in enumerate(_node_content["var"]):
            _node_editor_frame.alpha_composite(node_editor_patch[2][_ph][0], (30, 50+_ph_id*45))

    _out_link_number = len(_node_content["out-link"])
    if _out_link_number:
        # expand _node_editor_frame if this number > 3
        if _out_link_number > 3:
            _wp, _sp = 55, 5
            new_width = _out_link_number*55-5
            _n_img = Image.new("RGBA", (new_width, _node_editor_frame.height), color=(255, 255, 255, 0))
            _n_img.alpha_composite(_node_editor_frame, dest=((new_width-160)//2, 0))
        else:
            _wp, _sp = SPACING_CONSTANT[_out_link_number]
        _top = _node_editor_frame.height-25

        if hover_state == EDITOR_OUT_LINK_HOVERED:
            for _out_link_id, _out_link_name in enumerate(_node_content["out-link"]):
                if _node_content["out-link"][_out_link_name] is None:
                    if _out_link_name == hover_buffer_content:
                        _node_editor_frame.alpha_composite(node_editor_patch[3][_out_link_name][1], (_out_link_id*_wp, _top))
                    else:
                        _node_editor_frame.alpha_composite(node_editor_patch[3][_out_link_name][0], (_out_link_id*_wp, _top))
                else:
                    if _out_link_name == hover_buffer_content:
                        _node_editor_frame.alpha_composite(node_editor_patch[3][_out_link_name][3], (_out_link_id*_wp, _top))
                    else:
                        _node_editor_frame.alpha_composite(node_editor_patch[3][_out_link_name][2], (_out_link_id*_wp, _top))
        else:
            for _out_link_id, _out_link_name in enumerate(_node_content["out-link"].keys()):
                if _node_content["out-link"][_out_link_name] is None:
                    _node_editor_frame.alpha_composite(node_editor_patch[3][_out_link_name][0], (_out_link_id*_wp, _top))
                else:
                    _node_editor_frame.alpha_composite(node_editor_patch[3][_out_link_name][2], (_out_link_id*_wp, _top))

    return _node_editor_frame


def show_node_editor(_layer_3, _node_x, _node_y, _node_img, _editor_img):
    _new_cover = Image.new("RGBA", (_layer_3.width, _layer_3.height), color=(21, 0, 63, 150))
    _new_cover.alpha_composite(_node_img, (_node_x-20, _node_y-20-GRID_SIZE))
    _new_cover.alpha_composite(_editor_img, (_node_x+GRID_SIZE+20, _node_y-GRID_SIZE))
    return Image.alpha_composite(_layer_3, _new_cover)


def node_editor_hover(node_content, _node_editor_img):
    _editor_w = _node_editor_img.width / GRID_SIZE
    _editor_h = _node_editor_img.height / GRID_SIZE
    _editor_range = (node_content["x"], node_content["y"]+1, _editor_w + 1.5,  _editor_h)
    _editor_origin_x = node_content["x"] - 0.5 + _editor_w / 2
    _editor_origin_y = node_content["y"] + 1

    _editor_name_range = (_editor_origin_x, _editor_origin_y, 4, 0.75)

    _ph_range = dict()
    for _ph_id, _ph in enumerate(node_content["var"]):
        _ph_range[_ph] = (_editor_origin_x+0.75, _editor_origin_y-1.625-_ph_id*1.125, 3, 0.5)

    _out_link_range = dict()
    if len(node_content["out-link"]):
        _wd, _sp = FSA_SPACING_CONSTANT.get(len(node_content["out-link"]), (1.25, 0.125))
        for link_id, _link in enumerate(node_content["out-link"]):
            _out_link_range[_link] = (1.375+_wd*link_id+(_wd-1)*_sp+node_content["x"],
                                      _editor_origin_y-_editor_h,
                                      _wd, 0.75)

    return _editor_range, _editor_name_range, _ph_range, _out_link_range


def lay_link_cursor(prev_layer, _x, _y, _cursor_img):
    _p = prev_layer.copy()
    _p.alpha_composite(_cursor_img, (_x, _y))
    return _p


def get_line_dir(pt1, pt2):
    if pt1[0] == pt2[0]:
        if pt1[1] > pt2[1]:
            return "s", "v"
        else:
            return "n", "v"
    else:
        if pt1[0] > pt2[0]:
            return "w", "h"
        else:
            return "e", "h"


def draw_link_img(_link_stitches, _raw_coordinates):
    # use this like:
    # draw_link_img(self._link_stitches, [(-3, 8), (-4, 8), (-4, 7), (-3, 7), (-3, 9), (-2, 9), (-2, 8), (-3, 8)])

    _xs = [_pt[0] for _pt in _raw_coordinates]
    _ys = [_pt[1] for _pt in _raw_coordinates]
    _min_xs = min(_xs) * 40
    _max_ys = max(_ys) * 40
    _coordinates = [(round(_xs[_i] * 40-_min_xs + 30), round(_max_ys - _ys[_i] * 40 + 30)) for _i in range(len(_raw_coordinates))]
    _sharp_turns = []

    if len(_coordinates) > 3:
        _sharp_turns.append(8)
        for _cor_id in range(1, len(_coordinates)-1):
            if _coordinates[_cor_id][0] == _coordinates[_cor_id-1][0]:
                if abs(_coordinates[_cor_id][0]-_coordinates[_cor_id+1][0]) < 20 or abs(_coordinates[_cor_id][1]-_coordinates[_cor_id-1][1]) < 20:
                    _sharp_turns.append(0)
                else:
                    _sharp_turns.append(8)
            else:
                if abs(_coordinates[_cor_id][1]-_coordinates[_cor_id+1][1]) < 20 or abs(_coordinates[_cor_id][0]-_coordinates[_cor_id-1][0]) < 20:
                    _sharp_turns.append(0)
                else:
                    _sharp_turns.append(8)
        _sharp_turns.append(8)
    else:
        _sharp_turns = [8 for _ in _coordinates]

    _turning_points = [()]
    _line_range = []
    _turner_dirs = [""]
    _cor_prev = _coordinates[0]
    _cor_cur = ()
    _dir_prev = ""
    for _cor_id in range(1, len(_coordinates)):
        _cor_cur = _coordinates[_cor_id]
        line_dir, line_hv = get_line_dir(_cor_prev, _cor_cur)

        if line_dir == "n":
            _line_range.append(((_cor_prev[0]-2, _cor_prev[1]+_sharp_turns[_cor_id-1], _cor_cur[1]-_cor_prev[1]-_sharp_turns[_cor_id]-_sharp_turns[_cor_id-1]), line_hv))
        elif line_dir == "s":
            _line_range.append(((_cor_cur[0]-2, _cor_cur[1]+_sharp_turns[_cor_id], _cor_prev[1]-_cor_cur[1]-_sharp_turns[_cor_id]-_sharp_turns[_cor_id-1]), line_hv))
        elif line_dir == "w":
            _line_range.append(((_cor_cur[0]+_sharp_turns[_cor_id], _cor_cur[1]-2, _cor_prev[0]-_cor_cur[0]-_sharp_turns[_cor_id]-_sharp_turns[_cor_id-1]), line_hv))
        elif line_dir == "e":
            _line_range.append(((_cor_prev[0]+_sharp_turns[_cor_id-1], _cor_prev[1]-2, _cor_cur[0]-_cor_prev[0]-_sharp_turns[_cor_id]-_sharp_turns[_cor_id-1]), line_hv))

        if _dir_prev and _sharp_turns[_cor_id-1]:
            _turning_points.append((_cor_prev[0]-12, _cor_prev[1]-12))
            _turner_dirs.append(TURNER_KEYWORD[_dir_prev + line_dir])

        _dir_prev = line_dir
        _cor_prev = _cor_cur

    # arrow coordinate
    if _dir_prev == "n":
        _arrow_coordinate = (_cor_cur[0] - 5, _cor_cur[1] - 18)
    elif _dir_prev == "s":
        _arrow_coordinate = (_cor_cur[0] - 5, _cor_cur[1] + 4)
    elif _dir_prev == "w":
        _arrow_coordinate = (_cor_cur[0] + 4, _cor_cur[1] - 5)
    else:
        _arrow_coordinate = (_cor_cur[0] - 18, _cor_cur[1] - 5)

    # start drawing
    sz_x = round((max(_xs) - min(_xs)) * 40 + 60)
    sz_y = round((max(_ys) - min(_ys)) * 40 + 60)
    _nh_link = Image.new("RGBA", (sz_x, sz_y), (255, 255, 255, 0))
    _h_link = Image.new("RGBA", (sz_x, sz_y), (255, 255, 255, 0))

    # draw lines
    for _line, _dir in _line_range:
        _l_left = _line[2]
        if _l_left > 0:
            if _dir == "h":
                _x = _line[0]
                while _l_left > 200:
                    _nh_link.alpha_composite(_link_stitches[0]["h"][0], (_x, _line[1]))
                    _h_link.alpha_composite(_link_stitches[0]["h"][1], (_x, _line[1]))
                    _x += 200
                    _l_left -= 200
                _nh_link.alpha_composite(_link_stitches[0]["h"][0], (_x, _line[1]), (0, 0, _l_left, 5))
                _h_link.alpha_composite(_link_stitches[0]["h"][1], (_x, _line[1]), (0, 0, _l_left, 5))
            else:
                _y = _line[1]
                while _l_left > 200:
                    _nh_link.alpha_composite(_link_stitches[0]["v"][0], (_line[0], _y))
                    _h_link.alpha_composite(_link_stitches[0]["v"][1], (_line[0], _y))
                    _y += 200
                    _l_left -= 200
                _nh_link.alpha_composite(_link_stitches[0]["v"][0], (_line[0], _y), (0, 0, 5, _l_left))
                _h_link.alpha_composite(_link_stitches[0]["v"][1], (_line[0], _y), (0, 0, 5, _l_left))

    # draw turners
    for _t_id, _t in enumerate(_turning_points):
        if _turner_dirs[_t_id]:
            _nh_link.alpha_composite(_link_stitches[1][_turner_dirs[_t_id]][0], _t)
            _h_link.alpha_composite(_link_stitches[1][_turner_dirs[_t_id]][1], _t)

    # draw cursors
    _nh_link.alpha_composite(_link_stitches[2][_dir_prev][0], _arrow_coordinate)
    _h_link.alpha_composite(_link_stitches[2][_dir_prev][1], _arrow_coordinate)

    # give the hover boxes
    hover_box = []
    for _pt_id in range(len(_raw_coordinates)-1):
        box_x_min = min(_raw_coordinates[_pt_id][0], _raw_coordinates[_pt_id+1][0]) - 0.25
        box_x_max = max(_raw_coordinates[_pt_id][0], _raw_coordinates[_pt_id+1][0]) + 0.1
        box_y_min = min(_raw_coordinates[_pt_id][1], _raw_coordinates[_pt_id+1][1]) - 0.1
        box_y_max = max(_raw_coordinates[_pt_id][1], _raw_coordinates[_pt_id+1][1]) + 0.25
        hover_box.append((box_x_min, box_y_min, box_x_max, box_y_max))

    # make glowing links
    _nh_link_glowing = large_out_glow_gen(_nh_link, 2)  # that will make an edge of 32
    _nh_link_glowing = _nh_link_glowing.crop((32, 32, _nh_link_glowing.width-32, _nh_link_glowing.height-32))
    _nh_link_glowing.alpha_composite(_nh_link)

    _h_link_glowing = large_out_glow_gen(_h_link, 2)  # that will make an edge of 32
    _h_link_glowing = _h_link_glowing.crop((32, 32, _h_link_glowing.width-32, _h_link_glowing.height-32))
    _h_link_glowing.alpha_composite(_h_link)

    return (_nh_link, _h_link, _nh_link_glowing, _h_link_glowing), (min(_xs)-0.75, max(_ys)+0.75), hover_box


def draw_link_layer(_w, _h, _position, link_buffer: dict, hovered_link, selected_links):

    _layer = Image.new("RGBA", (_w, _h), color=(0, 0, 0, 0))
    for _id, link_id in enumerate(link_buffer):
        _selected = link_id in selected_links
        _hovered = link_id == hovered_link
        if _selected:
            if _hovered:
                _layer.alpha_composite(link_buffer[link_id][0][3], dest=(_position[_id][0], _position[_id][1]))
            else:
                _layer.alpha_composite(link_buffer[link_id][0][2], dest=(_position[_id][0], _position[_id][1]))
        else:
            if _hovered:
                _layer.alpha_composite(link_buffer[link_id][0][1], dest=(_position[_id][0], _position[_id][1]))
            else:
                _layer.alpha_composite(link_buffer[link_id][0][0], dest=(_position[_id][0], _position[_id][1]))

    return _layer
