# -*- coding: utf-8 -*-
# created at: 2022/9/21 22:21
# author    : Gao Kai
# Email     : gaosimin1@163.com


import copy
from gui.utilities import get_var_name
from interface.fsaVisualize import *
from math import floor
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


MODE_DEFAULT = 0
MODE_NODE_CREATE = 1
MODE_NODE_MOVE = 2
MODE_NODE_EDIT = 3
MODE_LINK_CREATE = 4
MODE_RUNNING = 5


class Canvas(QGraphicsView):
    resized = pyqtSignal()
    mouse_move = pyqtSignal(int, int)
    middle_mouse_move = pyqtSignal(int, int)
    right_mouse_click = pyqtSignal(int, int)
    left_mouse_click = pyqtSignal(int, int)
    left_mouse_press = pyqtSignal(int, int)
    left_mouse_move = pyqtSignal(int, int)
    left_mouse_double_click = pyqtSignal(int, int)
    delete_pressed = pyqtSignal()
    shift_pressed = pyqtSignal()
    shift_released = pyqtSignal()

    def __init__(self, master, *args):
        super(Canvas, self).__init__(*args)

        self.master = master
        self.ready = False
        self.pressed_button = None
        self.setMouseTracking(True)

        self.q_scene = QGraphicsScene()
        self.q_pix_item = QGraphicsPixmapItem()
        self.q_pix_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.q_scene.addItem(self.q_pix_item)
        self.setScene(self.q_scene)

        self.prev_mouse_pos = QPointF(0, 0)

    def draw_pixmap(self, pixmap):
        self.q_pix_item.setPixmap(pixmap.toqpixmap())

    def resizeEvent(self, a0: QResizeEvent) -> None:
        if self.ready:
            self.q_scene = QGraphicsScene()
            self.q_pix_item = QGraphicsPixmapItem()
            self.q_pix_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            self.q_scene.addItem(self.q_pix_item)
            self.setScene(self.q_scene)
            self.resized.emit()
        return super(Canvas, self).resizeEvent(a0)

    def mouseMoveEvent(self, a0: QMouseEvent):
        delta_pos = a0.position() - self.prev_mouse_pos
        self.prev_mouse_pos = a0.position()
        if self.ready:
            if a0.buttons() == Qt.MouseButton.MiddleButton:
                # this emits delta position rather than position, because position is seemingly unnecessary when you move the view around
                self.middle_mouse_move.emit(delta_pos.x(), delta_pos.y())
            elif a0.buttons() == Qt.MouseButton.LeftButton:
                self.left_mouse_move.emit(a0.position().x()-4, a0.position().y()-4)
            else:
                self.mouse_move.emit(a0.position().x()-4, a0.position().y()-4)
        return super(Canvas, self).mouseMoveEvent(a0)

    def mousePressEvent(self, a0: QMouseEvent):
        if self.ready:
            self.pressed_button = a0.buttons()
            if self.pressed_button == Qt.MouseButton.LeftButton:
                self.left_mouse_press.emit(a0.position().x()-4, a0.position().y()-4)
            elif a0.buttons() == Qt.MouseButton.MiddleButton:
                self.setCursor(Qt.CursorShape.SizeAllCursor)
        return super(Canvas, self).mousePressEvent(a0)

    def mouseReleaseEvent(self, a0: QMouseEvent):
        if self.ready:
            if self.pressed_button == Qt.MouseButton.LeftButton:
                self.left_mouse_click.emit(a0.position().x()-4, a0.position().y()-4)
            if self.pressed_button == Qt.MouseButton.RightButton:
                self.right_mouse_click.emit(a0.position().x()-4, a0.position().y()-4)
            elif self.pressed_button == Qt.MouseButton.MiddleButton:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        return super(Canvas, self).mouseReleaseEvent(a0)

    def keyPressEvent(self, a0: QKeyEvent):
        if self.ready:
            if a0.key() == Qt.Key.Key_Delete:
                self.delete_pressed.emit()
            elif a0.key() == Qt.Key.Key_Shift:
                self.shift_pressed.emit()

    def keyReleaseEvent(self, a0: QKeyEvent) -> None:
        if self.ready:
            if a0.key() == Qt.Key.Key_Shift:
                self.shift_released.emit()

    def mouseDoubleClickEvent(self, a0: QMouseEvent) -> None:
        if self.ready:
            if a0.buttons() == Qt.MouseButton.LeftButton:
                self.left_mouse_double_click.emit(a0.position().x()-4, a0.position().y()-4)
        return super(Canvas, self).mouseDoubleClickEvent(a0)


class FSAViewer(QWidget):

    def bulk_added(self, fsa_name, node_names, node_dict, list_ids, list_dict):
        self.exit_all_modes()
        if self.selected_fsa:
            self.mode = MODE_DEFAULT
            self.mode_buffer = list()
            self.selection_box_pt1 = tuple()
            self.selected_nodes[fsa_name] = set(node_names)

            if fsa_name == self.selected_fsa:
                for node_name in node_names:
                    node_content = node_dict[node_name]
                    self.node_buffer[node_name] = generate_node_buffer(node_name, node_content)
                    self._node_hover_box_check[node_name] = (node_content["x"], node_content["y"])
                    self._node_editor_patches[node_name] = update_node_editor_patches(node_name, node_content, self._node_editor_stitches, self._node_editor_pool)
                    self._node_editor_projection[node_name] = draw_node_editor(node_content, self._node_editor_patches[node_name], self._node_editor_hover_state, self._node_editor_buffer)
                    self._node_editor_hover_box_check[node_name] = node_editor_hover(node_content, self._node_editor_projection[node_name])

                for link_id in list_ids:
                    self._link_buffer[link_id] = draw_link_img(self._link_stitches, list_dict[link_id]["anchor"])

                self.draw_node_layer()
                self.draw_link_layer()
                self.composite_3_layers()
                self.graphic_pipeline[4] = self.graphic_pipeline[3]
                self.update_display()

    def bulk_node_move(self, fsa_name, node_names, dest, links_to_redraw):
        self.exit_all_modes()
        if self.selected_fsa:
            if fsa_name == self.selected_fsa:
                for node_id, node_name in enumerate(node_names):
                    node_content = self.guiMain.project.node_get_properties(node_name, fsa_name=fsa_name)[1]
                    self.node_buffer[node_name]["x"], self.node_buffer[node_name]["y"] = dest[node_id]
                    self._node_hover_box_check[node_name] = (self.node_buffer[node_name]["x"], self.node_buffer[node_name]["y"])
                    self._node_editor_hover_box_check[node_name] = node_editor_hover(node_content, self._node_editor_projection[node_name])

                for _link_id in links_to_redraw:
                    _link_content = self.guiMain.project.link_get_anchor_points(_link_id, fsa_name)
                    self._link_buffer[_link_id] = draw_link_img(self._link_stitches, _link_content)

                self.draw_node_layer()
                self.draw_link_layer()
                self.composite_3_layers()
                self.graphic_pipeline[4] = self.graphic_pipeline[3]
                self.update_display()

    def bulk_removed(self, fsa_name, node_names, link_ids):
        if self.selected_fsa:
            self.exit_all_modes()
            self.mode = MODE_DEFAULT
            self.mode_buffer = list()
            self.selection_box_pt1 = tuple()
            self.selected_nodes[fsa_name] = set()

            if fsa_name == self.selected_fsa:
                for node_name in node_names:
                    self.node_buffer.pop(node_name)
                    self._node_hover_box_check.pop(node_name)
                    self._node_editor_patches.pop(node_name)
                    self._node_editor_projection.pop(node_name)
                    self._node_editor_hover_box_check.pop(node_name)

                for link_id in link_ids:
                    self._link_buffer.pop(link_id)

                self.draw_node_layer()
                self.draw_link_layer()
                self.composite_3_layers()
                self.graphic_pipeline[4] = self.graphic_pipeline[3]
                self.update_display()

    def check_hover(self, _x, _y):
        _prev_hovered_node = self.hovered_node
        _prev_hovered_link = self.hovered_link
        _altered = False
        self.hovered_node = ""
        for _node_name, _bbox in self._node_hover_box_check.items():
            if _bbox[0] < _x < _bbox[0]+1 and _bbox[1] < _y < _bbox[1]+1:
                self.hovered_node = _node_name
                break

        if self.hovered_node != _prev_hovered_node:
            self.draw_node_layer()
            _altered = True

        self.hovered_link = None
        for _link_id, _link_content in self._link_buffer.items():
            _b_boxes = _link_content[2]
            for _b_box in _b_boxes:
                if _b_box[0] < _x < _b_box[2] and _b_box[1] < _y < _b_box[3]:
                    self.hovered_link = _link_id
                    break

        if self.hovered_link != _prev_hovered_link:
            self.draw_link_layer()
            _altered = True

        if _altered:
            self.composite_3_layers()
            self.graphic_pipeline[4] = self.graphic_pipeline[3]
            self.update_display()

    def check_node_edit_hover(self, _x, _y):
        _dont_quit = True
        _prev_state = self._node_editor_hover_state
        _prev_content = self._node_editor_buffer
        editor_hover_box = self._node_editor_hover_box_check[self.editing_node]

        if _x is not None:
            if editor_hover_box[0][0] < _x < editor_hover_box[0][0]+editor_hover_box[0][2] and editor_hover_box[0][1]-editor_hover_box[0][3] < _y < editor_hover_box[0][1]:
                self._node_editor_hover_state = EDITOR_HOVERED
                if editor_hover_box[1][0] < _x < editor_hover_box[1][0]+editor_hover_box[1][2] and editor_hover_box[1][1]-editor_hover_box[1][3] < _y < editor_hover_box[1][1]:
                    self._node_editor_hover_state = EDITOR_NODE_NAME_HOVERED
                    _dont_quit = False

                if _dont_quit:
                    for _ph_name, _bbox in editor_hover_box[2].items():
                        if _bbox[0] < _x < _bbox[0]+_bbox[2] and _bbox[1] < _y < _bbox[1]+_bbox[3]:
                            self._node_editor_hover_state = EDITOR_PH_HOVERED
                            self._node_editor_buffer = _ph_name
                            _dont_quit = False
                            break

                    if _dont_quit:
                        for _out_name, _bbox in editor_hover_box[3].items():
                            if _bbox[0] < _x < _bbox[0]+_bbox[2] and _bbox[1] < _y < _bbox[1]+_bbox[3]:
                                self._node_editor_hover_state = EDITOR_OUT_LINK_HOVERED
                                self._node_editor_buffer = _out_name
                                break

            else:
                self._node_editor_hover_state = EDITOR_NOT_HOVERED

        else:
            self._node_editor_hover_state = EDITOR_HOVERED
            self._node_editor_buffer = ()

        if _prev_state != self._node_editor_hover_state or _prev_content != self._node_editor_buffer:
            _node_content = self.guiMain.project.node_get_properties(self.editing_node, self.selected_fsa)[1]
            self._node_editor_projection[self.editing_node] = draw_node_editor(_node_content, self._node_editor_patches[self.editing_node], self._node_editor_hover_state, self._node_editor_buffer)
            self.graphic_pipeline[4] = show_node_editor(self.graphic_pipeline[3], self.node_buffer[self.editing_node]["px"], self.node_buffer[self.editing_node]["py"],
                                                        self._node_image_pool[self.node_buffer[self.editing_node]["type"]][2], self._node_editor_projection[self.editing_node])
            self.update_display()

    def closeEvent(self, a0: QCloseEvent) -> None:
        super(FSAViewer, self).closeEvent(a0)
        self.guiMain.actionFSA_Viewer.setChecked(False)

    def composite_3_layers(self):
        _temp = composite_2_layers(self.graphic_pipeline[0], self.graphic_pipeline[2])
        self.graphic_pipeline[3] = composite_2_layers(_temp, self.graphic_pipeline[1])

    def delete_selection(self):
        if self.mode == MODE_DEFAULT and not self.selection_box_pt1:
            self.guiMain.do("bulk-delete", self.selected_nodes[self.selected_fsa], self.selected_fsa, self.selected_links[self.selected_fsa])
            self.selected_nodes[self.selected_fsa] = set()
            self.selected_links[self.selected_fsa] = set()

    def draw2fsa_cvt(self, _x, _y):
        return round((_x - self.graphicsView.size().width() / 2 + 3) / GRID_SIZE + self.x, 6), \
               round((self.graphicsView.size().height() / 2 - 3 - _y) / GRID_SIZE + self.y, 6)

    def draw_background_layer(self, color=0):
        self.graphic_pipeline[0] = draw_background_display(
            self.graphicsView.size().width()-2, self.graphicsView.size().height()-2,
            self.x, self.y, color
        )

    def draw_fsa_deselected(self):
        _w = self.graphicsView.size().width()-2
        _h = self.graphicsView.size().height()-2
        if _w > 0 and _h > 0:
            self.graphic_pipeline[4] = draw_fsa_deselected_display(_w, _h)

    def draw_link_layer(self):
        ps = []
        for _link_id, _link_content in self._link_buffer.items():
            ps.append(self.fsa2draw_cvt(self._link_buffer[_link_id][1][0], self._link_buffer[_link_id][1][1]))
        self.graphic_pipeline[2] = draw_link_layer(self.graphicsView.size().width()-2, self.graphicsView.size().height()-2, ps,
                                                   self._link_buffer, self.hovered_link, self.selected_links[self.selected_fsa])

    def draw_node_layer(self):
        for _node in self.node_buffer.values():
            _node["px"], _node["py"] = self.fsa2draw_cvt(_node["x"], _node["y"])
        self.graphic_pipeline[1] = draw_node_layer(self.graphicsView.size().width()-2, self.graphicsView.size().height()-2,
                                                   self.node_buffer, self.hovered_node, self.selected_nodes[self.selected_fsa], self._node_image_pool, self.mode == MODE_NODE_MOVE)

    def enter_link_create_mode(self, _x, _y):
        # below are from self.check_hover()

        _prev_hovered_node = self.hovered_node
        self.hovered_node = ""
        for _node_name, _bbox in self._node_hover_box_check.items():
            if _bbox[0] < _x < _bbox[0]+1 and _bbox[1] < _y < _bbox[1]+1:
                self.hovered_node = _node_name
                break

        self.draw_node_layer()
        self.draw_link_layer()
        self.composite_3_layers()

        _x, _y = self.fsa2draw_cvt(_x, _y)
        self.mode = MODE_LINK_CREATE
        self.graphic_pipeline[4] = lay_link_cursor(self.graphic_pipeline[3], _x, _y, self._node_editor_patches[self.editing_node][4][self._node_editor_buffer])
        self.update_display()

    def enter_node_create_mode(self, node_class_name):
        self.mode = MODE_NODE_CREATE
        self.mode_buffer = [node_class_name, ]

    def enter_node_move_mode(self, _x, _y):
        self.mode = MODE_NODE_MOVE
        self.node_move_origin = (_x, _y)
        self.draw_node_layer()
        self.draw_link_layer()
        self.composite_3_layers()
        self.make_selected_node_graphic_combination(0, 0)
        self.update_display()

    def enter_run_mode(self):
        self.mode = MODE_RUNNING
        self.selected_nodes[self.selected_fsa] = set()
        self.selected_links[self.selected_fsa] = set()
        self.draw_background_layer(1)
        self.draw_node_layer()
        self.draw_link_layer()
        self.composite_3_layers()
        self.graphic_pipeline[4] = self.graphic_pipeline[3]
        self.update_display()

    def enter_node(self, node_name):
        self.selected_nodes[self.selected_fsa] = {node_name}
        self.x = self.node_buffer[node_name]["x"]+0.5
        self.y = self.node_buffer[node_name]["y"]-0.5

        self.fsa_position_buffer[self.selected_fsa] = (self.x, self.y)
        self._draw_fsa(1)
        self.update_display()

    def exit_run_mode(self):
        self.mode = MODE_DEFAULT
        self.selected_nodes[self.selected_fsa] = set()
        self.selected_links[self.selected_fsa] = set()
        self.draw_background_layer()
        self.draw_node_layer()
        self.draw_link_layer()
        self.composite_3_layers()
        self.graphic_pipeline[4] = self.graphic_pipeline[3]
        self.update_display()

    def exit_all_modes(self):
        if self.mode == MODE_NODE_EDIT:
            self.editing_node = ""
            self.mode = MODE_DEFAULT
        elif self.mode == MODE_NODE_MOVE:
            self.exit_node_move_mode(None, None)
        elif self.mode == MODE_NODE_CREATE:
            self.exit_node_create_mode()

    def exit_node_create_mode(self):
        self.mode = MODE_DEFAULT
        self.mode_buffer = []

    def exit_node_edit_mode(self, _x, _y):
        self.mode = MODE_DEFAULT
        self.editing_node = ""
        self.selected_nodes[self.selected_fsa] = set()
        self.check_hover(_x, _y)
        self.draw_node_layer()
        self.draw_link_layer()
        self.composite_3_layers()
        self.graphic_pipeline[4] = self.graphic_pipeline[3]
        self.update_display()

    def exit_node_move_mode(self, _x, _y=None):
        self.mode = MODE_DEFAULT
        self.draw_node_layer()
        self.node_move_origin = ()

        if _y is not None:
            _temp_nodes = list()
            _temp_new_position = list()
            for _node in self.selected_nodes[self.selected_fsa]:
                _temp_nodes.append(_node)
                _temp_new_position.append((self.node_buffer[_node]["x"] + _x, self.node_buffer[_node]["y"] + _y))
            self.guiMain.do("bulk_node_move", self.selected_fsa, _temp_nodes, _temp_new_position)

    def exit_link_create_mode(self):
        self.mode = MODE_DEFAULT

        self.guiMain.do("link-create", self.selected_fsa, self.editing_node, self._node_editor_buffer, self.hovered_node)
        self._node_editor_buffer = ""

        node_content = self.guiMain.project.node_get_properties(self.editing_node, self.selected_fsa)[1]
        self._node_editor_patches[self.editing_node] = update_node_editor_patches(self.editing_node, node_content, self._node_editor_stitches, self._node_editor_pool)
        self._node_editor_projection[self.editing_node] = draw_node_editor(node_content, self._node_editor_patches[self.editing_node],
                                                                           self._node_editor_hover_state, self._node_editor_buffer)

        self.editing_node = ""
        self.selected_nodes[self.selected_fsa] = set()

    def fsa2draw_cvt(self, _x, _y):
        return round((_x - self.x) * GRID_SIZE + self.graphicsView.size().width() / 2), \
               round(self.graphicsView.size().height() / 2 - (_y - self.y) * GRID_SIZE)

    def fsa_name_change(self, _old_name, _new_name):
        if _old_name in self.fsa_position_buffer:
            self.fsa_position_buffer[_new_name] = self.fsa_position_buffer[_old_name]
            self.selected_nodes[_new_name] = self.selected_nodes[_old_name]
            self.selected_links[_new_name] = self.selected_links[_old_name]
            self.fsa_position_buffer.pop(_old_name)
            self.selected_nodes.pop(_old_name)
            self.selected_links.pop(_old_name)

            if self.selected_fsa == _old_name:
                self.selected_fsa = _new_name
                self.setWindowTitle(f"FSA Viewer ({_new_name})")

    def left_mouse_click(self, _x, _y):
        _x, _y = self.draw2fsa_cvt(_x, _y)
        if self.mode == MODE_DEFAULT:
            if not self.shift_held:
                self.selected_nodes[self.selected_fsa] = set()
                self.selected_links[self.selected_fsa] = set()

            if self.selection_box_pt1:
                _x1, _x2 = min(self.selection_box_pt1[0], _x), max(self.selection_box_pt1[0], _x)
                _y1, _y2 = min(self.selection_box_pt1[1], _y), max(self.selection_box_pt1[1], _y)
                self.selection_box_pt1 = tuple()

                for _node_name, _node in self.node_buffer.items():
                    if _x1-1 < _node["x"] < _x2 and _y1-1 < _node["y"] < _y2:
                        if _node_name in self.selected_nodes[self.selected_fsa]:
                            self.selected_nodes[self.selected_fsa].remove(_node_name)
                        else:
                            self.selected_nodes[self.selected_fsa].add(_node_name)

                for _link_id, _link_content in self._link_buffer.items():
                    _b_boxes = _link_content[2]
                    for _b_box in _b_boxes:
                        if _x1 < _b_box[2] and _x2 > _b_box[0] and _y1 < _b_box[3] and _y2 > _b_box[1]:
                            if _link_id in self.selected_links[self.selected_fsa]:
                                self.selected_links[self.selected_fsa].remove(_link_id)
                            else:
                                self.selected_links[self.selected_fsa].add(_link_id)
                            break

            else:
                if self.hovered_node:
                    if self.hovered_node in self.selected_nodes[self.selected_fsa]:
                        self.selected_nodes[self.selected_fsa].remove(self.hovered_node)
                    else:
                        self.selected_nodes[self.selected_fsa].add(self.hovered_node)

                if self.hovered_link:
                    if self.hovered_link in self.selected_links[self.selected_fsa]:
                        self.selected_links[self.selected_fsa].remove(self.hovered_link)
                    else:
                        self.selected_links[self.selected_fsa].add(self.hovered_link)

            self.draw_node_layer()
            self.draw_link_layer()

            self.composite_3_layers()
            self.graphic_pipeline[4] = self.graphic_pipeline[3]
            self.update_display()

        elif self.mode == MODE_NODE_CREATE:
            self.guiMain.do("node-create", self.mode_buffer[0], self.selected_fsa, floor(_x), floor(_y))
            self.exit_node_create_mode()

        elif self.mode == MODE_NODE_MOVE:
            if round(floor(_x)-self.node_move_origin[0]) or round(floor(_y)-self.node_move_origin[1]):
                self.exit_node_move_mode(round(floor(_x)-self.node_move_origin[0]), round(floor(_y)-self.node_move_origin[1]))
            else:
                if self.hovered_node:
                    if self.hovered_node in self.selected_nodes[self.selected_fsa]:
                        self.selected_nodes[self.selected_fsa].remove(self.hovered_node)
                    else:
                        self.selected_nodes[self.selected_fsa].add(self.hovered_node)
                self.exit_node_move_mode(None, None)
            self.draw_node_layer()

            self.draw_link_layer()
            self.composite_3_layers()
            self.graphic_pipeline[4] = self.graphic_pipeline[3]
            self.update_display()

        elif self.mode == MODE_NODE_EDIT:
            if self._node_editor_hover_state == EDITOR_NOT_HOVERED:
                self.exit_node_edit_mode(_x, _y)
            else:
                if self._node_editor_hover_state == EDITOR_NODE_NAME_HOVERED:
                    _entered_name = QInputDialog.getText(self, "Node Name Change", "Enter a new name for the node:", text=self.editing_node)
                    if _entered_name[1]:
                        self.guiMain.do("node-rename", self.editing_node, _entered_name[0], self.selected_fsa)
                    self.check_node_edit_hover(None, None)
                elif self._node_editor_hover_state == EDITOR_PH_HOVERED:
                    _node_content = self.guiMain.project.node_get_properties(self.editing_node, self.selected_fsa)[1]
                    _var_type = _node_content["var"][self._node_editor_buffer]["type"]
                    _var_list = self.guiMain.project.get_certain_type_var_list(_var_type)
                    _sel, _ret = get_var_name(_var_list, self._var_image_pool[_var_type], _node_content["var"][self._node_editor_buffer]["name"])
                    if _ret:
                        self.guiMain.do("node-set-var", self.editing_node, self._node_editor_buffer, _sel, self.selected_fsa)
                    self.check_node_edit_hover(None, None)
                elif self._node_editor_hover_state == EDITOR_OUT_LINK_HOVERED:
                    self.enter_link_create_mode(_x, _y)

        elif self.mode == MODE_LINK_CREATE:
            self.exit_link_create_mode()

    def left_mouse_double_click(self, _x, _y):
        if self.mode == MODE_DEFAULT:
            if self.hovered_node:
                self.mode = MODE_NODE_EDIT
                self._node_editor_hover_state = EDITOR_HOVERED
                node_content = self.guiMain.project.node_get_properties(self.hovered_node, self.selected_fsa)[1]
                self._node_editor_projection[self.hovered_node] = draw_node_editor(node_content, self._node_editor_patches[self.hovered_node], self._node_editor_hover_state, self._node_editor_buffer)
                self.graphic_pipeline[4] = show_node_editor(self.graphic_pipeline[3], self.node_buffer[self.hovered_node]["px"], self.node_buffer[self.hovered_node]["py"],
                                                            self._node_image_pool[self.node_buffer[self.hovered_node]["type"]][2], self._node_editor_projection[self.hovered_node])
                self.editing_node = self.hovered_node
                self.update_display()

    def left_mouse_press(self, _x, _y):
        _x, _y = self.draw2fsa_cvt(_x, _y)
        if self.mode == MODE_DEFAULT:
            if self.hovered_node not in self.selected_nodes[self.selected_fsa]:
                self.selection_box_pt1 = (_x, _y)
            else:
                self.enter_node_move_mode(floor(_x), floor(_y))

    def left_mouse_move(self, _x, _y):
        if self.mode == MODE_DEFAULT:
            if self.selection_box_pt1:
                _p1x, _p1y = self.fsa2draw_cvt(self.selection_box_pt1[0], self.selection_box_pt1[1])
                _p1x, _p2x = min(_p1x, _x), max(_p1x, _x)
                _p1y, _p2y = min(_p1y, _y), max(_p1y, _y)

                self.graphic_pipeline[4] = add_selection_bbox(self.graphic_pipeline[3], _p1x, _p1y, _p2x, _p2y)
                self.update_display()
        elif self.mode == MODE_NODE_MOVE:
            _x, _y = self.draw2fsa_cvt(_x, _y)
            _x, _y = round(floor(_x)-self.node_move_origin[0]), round(floor(_y)-self.node_move_origin[1])
            self.make_selected_node_graphic_combination(_x, _y)
            self.update_display()

    def link_added(self, _link_id, _link_content, _fsa_name):
        if _fsa_name == self.selected_fsa:
            self._link_buffer[_link_id] = draw_link_img(self._link_stitches, _link_content)
            self.draw_link_layer()
            self.composite_3_layers()
            self.graphic_pipeline[4] = self.graphic_pipeline[3]
            self.update_display()

    def link_removed(self, _link_id, _fsa_name):
        if _fsa_name == self.selected_fsa:
            self._link_buffer.pop(_link_id)
            self.draw_link_layer()
            self.composite_3_layers()
            self.graphic_pipeline[4] = self.graphic_pipeline[3]
            self.update_display()

    def make_selected_node_graphic_combination(self, offset_x, offset_y):
        _temp_dict = dict()
        for _node_name in self.selected_nodes[self.selected_fsa]:
            _temp_dict[_node_name] = copy.deepcopy(self.node_buffer[_node_name])
            _node = _temp_dict[_node_name]
            _node["px"], _node["py"] = self.fsa2draw_cvt(_node["x"]+offset_x, _node["y"]+offset_y)
        _temp_graph = draw_node_layer(self.graphicsView.size().width()-2, self.graphicsView.size().height()-2,
                                      _temp_dict, self.selected_nodes[self.selected_fsa], self.selected_nodes[self.selected_fsa], self._node_image_pool)
        self.graphic_pipeline[4] = composite_2_layers(self.graphic_pipeline[3], _temp_graph)

    def mouse_move(self, _x, _y):
        _x, _y = self.draw2fsa_cvt(_x, _y)
        if self.mode == MODE_DEFAULT:
            self.check_hover(_x, _y)
        elif self.mode == MODE_NODE_CREATE:
            _x, _y = self.fsa2draw_cvt(floor(_x), floor(_y))
            self.graphic_pipeline[4] = put_image_by_xy(self.graphic_pipeline[3], _x, _y, self._node_image_pool[self.mode_buffer[0]][4])
            self.update_display()
        elif self.mode == MODE_NODE_EDIT:
            self.check_node_edit_hover(_x, _y)
        elif self.mode == MODE_LINK_CREATE:
            # below are from self.check_hover()

            _prev_hovered_node = self.hovered_node
            self.hovered_node = ""
            for _node_name, _bbox in self._node_hover_box_check.items():
                if _bbox[0] < _x < _bbox[0]+1 and _bbox[1] < _y < _bbox[1]+1:
                    self.hovered_node = _node_name
                    break

            if self.hovered_node != _prev_hovered_node:
                self.draw_node_layer()

            self.composite_3_layers()
            _x, _y = self.fsa2draw_cvt(_x, _y)
            self.graphic_pipeline[4] = lay_link_cursor(self.graphic_pipeline[3], _x, _y, self._node_editor_patches[self.editing_node][4][self._node_editor_buffer])
            self.update_display()

    def node_added(self, fsa_name, node_name, node_content):
        if fsa_name == self.selected_fsa:
            self.node_buffer[node_name] = generate_node_buffer(node_name, node_content)
            self._node_hover_box_check[node_name] = (node_content["x"], node_content["y"])
            self._node_editor_patches[node_name] = update_node_editor_patches(node_name, node_content, self._node_editor_stitches, self._node_editor_pool)
            self._node_editor_projection[node_name] = draw_node_editor(node_content, self._node_editor_patches[node_name], self._node_editor_hover_state, self._node_editor_buffer)
            self._node_editor_hover_box_check[node_name] = node_editor_hover(node_content, self._node_editor_projection[node_name])

            related_links = list(node_content["in-link"]) + list(node_content["out-link"].values())

            for link_id in related_links:
                if link_id is not None:
                    _link_content = self.guiMain.project.link_get_anchor_points(link_id, self.selected_fsa)
                    self._link_buffer[link_id] = draw_link_img(self._link_stitches, _link_content)
                    self.draw_link_layer()

            self.draw_node_layer()
            self.draw_link_layer()
            self.composite_3_layers()
            self.graphic_pipeline[4] = self.graphic_pipeline[3]
            self.update_display()

    def node_removed(self, fsa_name: str, node_name: str, related_links: list):
        self.exit_all_modes()

        if fsa_name == self.selected_fsa:
            self.node_buffer.pop(node_name)
            self._node_hover_box_check.pop(node_name)
            self._node_editor_patches.pop(node_name)
            self._node_editor_projection.pop(node_name)
            self._node_editor_hover_box_check.pop(node_name)

            if node_name in self.selected_nodes[self.selected_fsa]:
                self.selected_nodes[self.selected_fsa].remove(node_name)

            self.draw_node_layer()

            for _link_id in related_links:
                self._link_buffer.pop(_link_id)

            self.draw_link_layer()
            self.composite_3_layers()
            self.graphic_pipeline[4] = self.graphic_pipeline[3]
            self.update_display()

    def node_rename(self, old_name, new_name, fsa_name):
        if fsa_name == self.selected_fsa:
            _node_content = self.guiMain.project.node_get_properties(new_name, fsa_name)[1]
            self.node_buffer[new_name] = generate_node_buffer(new_name, _node_content)
            self.node_buffer.pop(old_name)
            self.draw_node_layer()
            self.composite_3_layers()
            self._node_editor_patches[new_name] = update_node_editor_patches(new_name, _node_content, self._node_editor_stitches, self._node_editor_pool)
            self._node_editor_projection[new_name] = draw_node_editor(_node_content, self._node_editor_patches[new_name], self._node_editor_hover_state, self._node_editor_buffer)
            self._node_editor_hover_box_check[new_name] = self._node_editor_hover_box_check[old_name]
            self._node_hover_box_check[new_name] = self._node_hover_box_check[old_name]
            self._node_editor_patches.pop(old_name)
            self._node_editor_projection.pop(old_name)
            self._node_editor_hover_box_check.pop(old_name)
            self._node_hover_box_check.pop(old_name)

            if self.mode == MODE_NODE_EDIT and self.editing_node == old_name:
                self.editing_node = new_name
                self.graphic_pipeline[4] = show_node_editor(self.graphic_pipeline[3], self.node_buffer[self.editing_node]["px"], self.node_buffer[self.editing_node]["py"],
                                                            self._node_image_pool[self.node_buffer[self.editing_node]["type"]][2], self._node_editor_projection[self.editing_node])
            else:
                self.graphic_pipeline[4] = self.graphic_pipeline[3]

            self.update_display()

    def open_project(self, _name, _m: dict):
        self.guiMain.interface.fsa_selected.connect(self._fsa_selected)

    def parse_fsa(self, _fsa_name):
        self.mode = MODE_DEFAULT
        self.mode_buffer = list()

        self.selected_fsa = _fsa_name
        self.node_buffer = dict()
        self._link_buffer = dict()
        self._node_hover_box_check = dict()
        self._node_editor_patches = dict()
        self._node_editor_projection = dict()
        self._node_editor_hover_box_check = dict()

        if _fsa_name not in self.selected_nodes:
            self.selected_nodes[_fsa_name] = set()
            self.selected_links[_fsa_name] = set()

        self.hovered_node = ""

        if _fsa_name:
            fsa_nodes = self.guiMain.project.node_list(_fsa_name)
            for node_name in fsa_nodes:
                node_content = self.guiMain.project.node_get_properties(node_name, fsa_name=_fsa_name)[1]
                self.node_buffer[node_name] = generate_node_buffer(node_name, node_content)
                self._node_hover_box_check[node_name] = (node_content["x"], node_content["y"])
                self._node_editor_patches[node_name] = update_node_editor_patches(node_name, node_content, self._node_editor_stitches, self._node_editor_pool)
                self._node_editor_projection[node_name] = draw_node_editor(node_content, self._node_editor_patches[node_name], self._node_editor_hover_state, self._node_editor_buffer)
                self._node_editor_hover_box_check[node_name] = node_editor_hover(node_content, self._node_editor_projection[node_name])

            fsa_links = self.guiMain.project.link_list(_fsa_name)
            for link_id in fsa_links:
                link_anchors = self.guiMain.project.link_get_anchor_points(link_id, fsa_name=_fsa_name)
                self._link_buffer[link_id] = draw_link_img(self._link_stitches, link_anchors)

    def ph_set_var(self, node_name, placeholder_name, var_name, fsa_name):
        if fsa_name == self.selected_fsa:
            _node_content = self.guiMain.project.node_get_properties(node_name, fsa_name)[1]
            self._node_editor_patches[node_name] = update_node_editor_patches(node_name, _node_content, self._node_editor_stitches, self._node_editor_pool)
            self._node_editor_projection[node_name] = draw_node_editor(_node_content, self._node_editor_patches[node_name], self._node_editor_hover_state, self._node_editor_buffer)

            if self.mode == MODE_NODE_EDIT and self.editing_node == node_name:
                self.graphic_pipeline[4] = show_node_editor(self.graphic_pipeline[3], self.node_buffer[self.editing_node]["px"], self.node_buffer[self.editing_node]["py"],
                                                            self._node_image_pool[self.node_buffer[self.editing_node]["type"]][2], self._node_editor_projection[self.editing_node])
                self.update_display()

    def right_mouse_click(self, _x, _y):
        if self.mode == MODE_NODE_CREATE:
            self.mode = MODE_DEFAULT
            self.mode_buffer = list()
            self.graphic_pipeline[4] = self.graphic_pipeline[3]
            self.update_display()

    def shift_hold_on(self):
        self.shift_held = True

    def shift_hold_off(self):
        self.shift_held = False

    def show(self):
        super(FSAViewer, self).show()
        self.guiMain.actionFSA_Viewer.setChecked(True)

    def update_display(self):
        if self.graphic_pipeline[4] is not None:
            self.graphicsView.draw_pixmap(self.graphic_pipeline[4])

    def update_node_image_pool(self, _icon_path: str, _node_class_dict: dict):
        self._node_image_pool = load_node_icon(_icon_path, _node_class_dict)
        self._node_editor_stitches = draw_node_editor_stitches()
        self._node_editor_pool = draw_node_editor_general_parts(_node_class_dict, self._var_image_pool, self._node_editor_stitches)
        self._link_stitches = draw_link_stitches()

    def update_var_image_pool(self, _icon_path: str, _var_class_dict: dict):
        self._var_image_pool = load_var_icon(_icon_path, _var_class_dict)

    def var_renamed(self, _, new_name):
        _quote = self.guiMain.project.var_quote_lookup(new_name)
        for _quote_item in _quote:
            if _quote_item[2] == self.selected_fsa:
                _node_content = self.guiMain.project.node_get_properties(_quote_item[1], self.selected_fsa)[1]
                self._node_editor_patches[_quote_item[1]] = update_node_editor_patches(_quote_item[1], _node_content, self._node_editor_stitches, self._node_editor_pool)
                self._node_editor_projection[_quote_item[1]] = draw_node_editor(_node_content, self._node_editor_patches[_quote_item[1]], self._node_editor_hover_state, self._node_editor_buffer)

                if self.mode == MODE_NODE_EDIT and self.editing_node == _quote_item[1]:
                    self.graphic_pipeline[4] = show_node_editor(self.graphic_pipeline[3], self.node_buffer[self.editing_node]["px"], self.node_buffer[self.editing_node]["py"],
                                                                self._node_image_pool[self.node_buffer[self.editing_node]["type"]][2], self._node_editor_projection[self.editing_node])
        self.update_display()

    def view_point_transform(self, delta_x, delta_y):
        # delta_x and delta_y are in pixels
        if self.selected_fsa:
            self.x -= delta_x / GRID_SIZE
            self.y += delta_y / GRID_SIZE
            self.x = round(self.x, 6)
            self.y = round(self.y, 6)
            self.fsa_position_buffer[self.selected_fsa] = (self.x, self.y)
            self._draw_fsa()

            if self.mode == MODE_NODE_EDIT:
                self.graphic_pipeline[4] = show_node_editor(self.graphic_pipeline[3], self.node_buffer[self.editing_node]["px"], self.node_buffer[self.editing_node]["py"],
                                                            self._node_image_pool[self.node_buffer[self.editing_node]["type"]][2], self._node_editor_projection[self.editing_node])

            self.update_display()

    def _draw_fsa(self, _c=0):
        self.draw_background_layer(_c)
        self.draw_node_layer()
        self.draw_link_layer()
        self.composite_3_layers()
        self.graphic_pipeline[4] = self.graphic_pipeline[3]

    def _fsa_selected(self, _name):
        self.parse_fsa(_name)
        if _name:
            self.setWindowTitle(f"FSA Viewer ({_name})")
            if _name not in self.fsa_position_buffer:
                self.fsa_position_buffer[_name] = (0, 0)
            self.x, self.y = self.fsa_position_buffer[_name]
            self._draw_fsa()
        else:
            self.setWindowTitle("FSA Viewer (None)")
            self.draw_fsa_deselected()

        self.update_display()

    def _resized(self):
        _w = self.graphicsView.size().width()-2
        _h = self.graphicsView.size().height()-2
        if _w > 0 and _h > 0:
            if self.selected_fsa:
                self._draw_fsa()
                if self.mode == MODE_NODE_EDIT:
                    self.graphic_pipeline[4] = show_node_editor(self.graphic_pipeline[3], self.node_buffer[self.editing_node]["px"], self.node_buffer[self.editing_node]["py"],
                                                                self._node_image_pool[self.node_buffer[self.editing_node]["type"]][2], self._node_editor_projection[self.editing_node])
                    self.update_display()

            else:
                self.draw_fsa_deselected()
            self.update_display()

    def __init__(self, gui_main):

        super(FSAViewer, self).__init__()
        self.guiMain = gui_main
        self.setWindowIcon(gui_main.icon)
        self.setObjectName(u"FSAViewer")
        self.resize(640, 480)
        self.move(470, 60)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.graphicsView = Canvas(self)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setMouseTracking(True)

        self.verticalLayout.addWidget(self.graphicsView)
        self.setWindowTitle("FSA Viewer (None)")

        self.graphicsView.ready = True
        self.graphicsView.resized.connect(self.update_display)
        self.graphicsView.resized.connect(self._resized)

        self.fsa_position_buffer = dict()

        self.selection_box_pt1 = tuple()

        self.selected_fsa = ""
        self.mode = MODE_DEFAULT
        self.mode_buffer = []
        self.shift_held = False

        self.selected_nodes = dict()
        self.hovered_node = ""
        self.editing_node = ""
        self.editing_link = ""

        self.node_buffer = dict()
        self._node_editor_patches = dict()

        self.graphic_pipeline = [
            None,              # background layer
            None,              # nodes layer
            None,              # link layer
            # the above three layers are parallel, once some of them are altered, then below layers are altered

            None,              # integrated layer of background layer, nodes layer and link layer
            None               # final version including selection images, creation images, node-editing images, etc.
        ]
        self.node_move_origin = ()

        self.x = 0
        self.y = 0

        self._node_image_pool = dict()
        self._var_image_pool = dict()

        self._node_hover_box_check = dict()
        # (x,y,w,h): (type, name)

        self._node_editor_pool = dict()          # node class name -> node class editor image
        self._node_editor_stitches = dict()
        self._node_editor_projection = dict()    # node name -> node editor buffer
        self._node_editor_hover_state = EDITOR_NOT_HOVERED
        self._node_editor_buffer = ()
        self._node_editor_hover_box_check = dict()
        self._link_stitches = ()
        self._link_buffer = dict()

        self.hovered_link = None
        self.selected_links = dict()

        # below is to establish all connections between canvas and project
        self.graphicsView.mouse_move.connect(self.mouse_move)
        self.graphicsView.shift_pressed.connect(self.shift_hold_on)
        self.graphicsView.shift_released.connect(self.shift_hold_off)
        self.graphicsView.left_mouse_click.connect(self.left_mouse_click)
        self.graphicsView.left_mouse_move.connect(self.left_mouse_move)
        self.graphicsView.left_mouse_press.connect(self.left_mouse_press)
        self.graphicsView.middle_mouse_move.connect(self.view_point_transform)
        self.graphicsView.right_mouse_click.connect(self.right_mouse_click)
        self.graphicsView.delete_pressed.connect(self.delete_selection)
        self.graphicsView.left_mouse_double_click.connect(self.left_mouse_double_click)
