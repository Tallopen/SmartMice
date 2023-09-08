# -*- coding: utf-8 -*-
# created at: 2022/6/29 16:09
# author    : Gao Kai
# Email     : gaosimin1@163.com

import copy
import importlib
import os.path
import pickle
import re

import core.interface
import core.runner as runner
import shutil
import sys
import time


def name_check(name):
    # if the name is camel case or underscore case, return True
    # else return false
    if re.match(r"^[a-zA-Z][a-zA-Z0-9]*(?:_[a-zA-Z0-9]+)*$", name):
        return True
    else:
        return False


def loose_name_check(name):
    # this name checker is looser, words connected with -, _ or spacing are all allowed
    if re.match(r"^[a-zA-Z][a-zA-Z0-9]*(?:[_\s\-][a-zA-Z0-9]+)*$", name):
        return True
    else:
        return False


def operation(f):

    def op_func(self, *args, **kwargs):
        _b, _m = f(self, *args, **kwargs)
        if _b:
            self.is_saved = False
        return _b, _m

    return op_func


def simple_connection(x0, y0, out_pt_id, out_pt_num, xn, yn):
    x0 = x0 + (out_pt_id + 1) / (out_pt_num + 1)
    xn += 0.5
    yn += 1

    # middle pts
    if y0 - yn >= 2:
        if x0 == xn:
            return [(x0, y0), (xn, yn)]
        else:
            md1 = (x0, (y0+yn)/2)
            md2 = (xn, (y0+yn)/2)
            return [(x0, y0), md1, md2, (xn, yn)]
    else:
        if abs(x0 - xn) >= 2:
            md1 = (x0, y0 - 0.75)
            md2 = ((x0+xn)/2, y0 - 0.75)
            md3 = ((x0+xn)/2, yn + 0.75)
            md4 = (xn, yn + 0.75)
        elif x0 - xn > 0:
            md1 = (x0, y0 - 0.75)
            md2 = (x0 + 2, y0 - 0.75)
            md3 = (x0 + 2, yn + 0.75)
            md4 = (xn, yn + 0.75)
        else:
            md1 = (x0, y0 - 0.75)
            md2 = (x0 - 2, y0 - 0.75)
            md3 = (x0 - 2, yn + 0.75)
            md4 = (xn, yn + 0.75)
        return [(x0, y0), md1, md2, md3, md4, (xn, yn)]


class Project:

    @operation
    def bulk_add(self, names, check_existence, links=None, fsa_name=None):
        """
        add a node that already exists into selected FSA
        :param names: the name of node
        :param check_existence: whether to check if the variable exists in node pool of FSA
        :param fsa_name: name of fsa, default selected fsa
        :param links: links attached to the node, default will be link ids quoted in the node
        :return:
        (True, None) - node successfully added
        (False, "Message") - node addition failed, message returned
        """
        if check_existence:
            fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
            if fsa_name is None:
                return False, "FSA is not designated."

        _selected_fsa = self._m["fsa"][fsa_name]
        _node_added = []

        if links is None:
            _link2add = []
        else:
            _link2add = links

        for name in names:
            if name not in _selected_fsa["node-index"]:
                _selected_fsa["node-index"].add(name)
                _node_added.append(name)

                _link2add += list(_selected_fsa["node"][name]["out-link"].values())
                _link2add += list(_selected_fsa["node"][name]["out-link"].values())

        _link2add = set(_link2add)
        if None in _link2add:
            _link2add.remove(None)

        for _link_id in _link2add:
            _this_link = _selected_fsa["link"][_link_id]
            _selected_fsa["link-index"].add(_link_id)
            _from_node = _selected_fsa["node"][_this_link["from"]]
            _to_node = _selected_fsa["node"][_this_link["to"]]
            _this_link["anchor"] = simple_connection(
                _from_node["x"], _from_node["y"],
                self._node_class[_from_node["type"]].out_enum[_this_link["output"]], self._node_class[_from_node["type"]].out_num,
                _to_node["x"], _to_node["y"]
            )

            _from_node["out-link"][_this_link["output"]] = _link_id
            _to_node["in-link"].add(_link_id)

        self.interface.bulk_added.emit(fsa_name, _node_added, _selected_fsa["node"], _link2add, _selected_fsa["link"])

        return True, None

    @operation
    def bulk_node_move(self, names, dest, fsa_name=None):
        """
        alter property value of a node
        :param names: list of node name
        :param dest: list of node move destination in tuple
        :param fsa_name: name of fsa, default selected fsa
        :return:
        (True, Original Value) - node successfully moved, original position returned
        (False, "Message") - Failed changing property, message returned
        """
        fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
        if fsa_name is None:
            return False, "FSA is not designated."
        _selected_fsa = self._m["fsa"][fsa_name]

        _original_values = []

        for _id, name in enumerate(names):
            if name in _selected_fsa["node-index"]:

                _original_values.append((_selected_fsa["node"][name]["x"], _selected_fsa["node"][name]["y"]))
                _selected_fsa["node"][name]["x"] = dest[_id][0]
                _selected_fsa["node"][name]["y"] = dest[_id][1]

            else:
                _original_values.append(())

        _link2move = []

        for name in names:

            _link2move += list(_selected_fsa["node"][name]["in-link"])
            _link2move += list(_selected_fsa["node"][name]["out-link"].values())

        _link2move = set(_link2move)

        if None in _link2move:
            _link2move.remove(None)

        for _link_id in _link2move:
            _this_link = _selected_fsa["link"][_link_id]
            _from_node = _selected_fsa["node"][_this_link["from"]]
            _to_node = _selected_fsa["node"][_this_link["to"]]
            _this_link["anchor"] = simple_connection(
                _from_node["x"], _from_node["y"],
                self._node_class[_from_node["type"]].out_enum[_this_link["output"]], self._node_class[_from_node["type"]].out_num,
                _to_node["x"], _to_node["y"]
            )

        self.interface.bulk_move.emit(fsa_name, names, dest, _link2move)

        return True, _original_values

    @operation
    def bulk_remove(self, nodes=None, links=None, fsa_name=None):
        """
        remove a node from selected FSA
        :param nodes: names of node to remove
        :param links: id of additional links to remove
        :param fsa_name: name of fsa, default selected fsa
        :return:
        (True, Coupled Links) - node successfully removed
        (False, "Message") - node removal failed, message returned
        """
        fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
        if fsa_name is None:
            return False, "FSA is not designated."
        _selected_fsa = self._m["fsa"][fsa_name]

        if links is None:
            _link_to_remove = []
        else:
            _link_to_remove = list(links)

        nodes_removed = []
        if nodes:
            for name in nodes:
                if name in _selected_fsa["node-index"]:
                    _selected_fsa["node-index"].remove(name)

                    _link_to_remove += list(_selected_fsa["node"][name]["out-link"].values())
                    _link_to_remove += list(_selected_fsa["node"][name]["in-link"])

                    nodes_removed.append(name)

        _link_to_remove = set(_link_to_remove)
        if None in _link_to_remove:
            _link_to_remove.remove(None)

        for link_id in _link_to_remove:
            _current_link = _selected_fsa["link"][link_id]
            _selected_fsa["node"][_current_link["from"]]["out-link"][_current_link["output"]] = None
            _selected_fsa["node"][_current_link["to"]]["in-link"].remove(link_id)
            _selected_fsa["link-index"].remove(link_id)

        self.interface.bulk_removed.emit(fsa_name, nodes_removed, _link_to_remove)

        return True, _link_to_remove

    def clear_memory(self):
        """
        clear all unquoted elements in the project
        """

        # discard unquoted fsa
        _new_fsa_dict = dict()
        for _key in self._m["fsa-index"]:
            _new_fsa_dict[_key] = self._m["fsa"][_key]
        self._m["fsa"] = _new_fsa_dict

        # unquoted records
        _new_record_dict = dict()
        for _record_name in self._m["record-index"]:
            _new_record_dict[_record_name] = self._m["record"][_record_name]
        self._m["record"] = _new_record_dict

        for _fsa_name in self._m["fsa"]:
            _fsa = self._m["fsa"][_fsa_name]

            _new_node_dict = dict()
            for _node in _fsa["node-index"]:
                _new_node_dict[_node] = _fsa["node"][_node]

            _new_link_dict = dict()
            for _link in _fsa["link-index"]:
                _new_link_dict[_link] = _fsa["link"][_link]

            _new_note_dict = dict()
            for _note in _fsa["note-index"]:
                _new_note_dict[_note] = _fsa["note"][_note]

            _fsa["node"] = _new_node_dict
            _fsa["link"] = _new_link_dict
            _fsa["note"] = _new_note_dict

    @operation
    def fsa_add(self, name, check_existence=True):
        """
        add an FSA that already exists into project pool
        :param name: the name of FSA
        :param check_existence: whether to check if the FSA exists in _m
        :return:
        (True, None) - fsa successfully added
        (False, "Message") - fsa addition failed, message returned
        """
        if check_existence:
            if name not in self._m["fsa"]:
                return False, "There is no FSA named '" + name + "'."
        if name not in self._m["fsa-index"]:
            self._m["fsa-index"].add(name)
            self.interface.fsa_added.emit(name)
            self.fsa_select(name)
            _selected_fsa = self._m["fsa"][name]

            for node_name in _selected_fsa["node-index"]:
                for placeholder_name, ph_content in _selected_fsa["node"][node_name]["var"].items():
                    if ph_content["name"]:
                        self._m["var"][ph_content["name"]]["quote"].add(str([placeholder_name, node_name, name]))

            return True, None
        else:
            return False, "FSA already present"

    @operation
    def fsa_duplicate(self, prev_name):
        """
        This duplicates a designated fsa
        :param prev_name: FSA name
        :return:
        (True, None) - fsa successfully created
        (False, "Message") - fsa creation failed, message returned
        """
        if prev_name not in self._m["fsa-index"]:
            return False, f"FSA {prev_name} is not in use."

        _new_fsa = copy.deepcopy(self._m["fsa"][prev_name])

        _new_name = prev_name + "_Copy_1"
        _new_name_index = 2
        while _new_name in self._m["fsa"]:
            _new_name = prev_name + "_Copy_" + str(_new_name_index)
            _new_name_index += 1

        for node_name in _new_fsa["node-index"]:
            for placeholder_name, ph_content in _new_fsa["node"][node_name]["var"].items():
                if ph_content["name"]:
                    self._m["var"][ph_content["name"]]["quote"].add(str([placeholder_name, node_name, _new_name]))

        _new_fsa["props"]["name"] = _new_name
        _new_fsa["props"]["creation-time"] = time.strftime("%Y%m%d-%H%M%S", time.localtime(time.time()))
        self._m["fsa"][_new_name] = _new_fsa
        self.fsa_add(_new_name)

        return True, _new_name

    def fsa_list(self):
        """
        list all FSAs in use
        :return: all names of FSA in use
        """
        return list(self._m["fsa-index"])

    @operation
    def fsa_new(self, **kwargs):
        """
        create a new FSA
        :param kwargs:
        -name           name of FSA, default is fsa+"fsa_index"
        :return:
        (True, None) - fsa successfully created
        (False, "Message") - fsa creation failed, message returned
        """

        _name = kwargs.get("name", "fsa" + str(self._m["fsa-i"]))

        if "name" not in kwargs:
            while _name in self._m["fsa"]:
                self._m["fsa-i"] += 1
                _name = "fsa" + str(self._m["fsa-i"])

        elif not name_check(_name):
            return False, "Name must be camel case or underscore case"

        if _name not in self._m["fsa"]:

            _fsa = {
                "node-index": set(),           # used nodes' index in dictionary "node"
                "link-index": set(),           # used links' index in dictionary "link"
                "note-index": set(),           # used notes' index in dictionary "note"

                # components of the fsa
                "node": {},
                "link": {},
                "note": {},

                # ids to create default name of nodes, or default number of links or notes
                "node-i": 1,
                "link-i": 1,
                "note-i": 1,

                "props": {
                    "name": _name,
                    "experimenter": "",
                    "creation-time": time.strftime("%Y%m%d-%H%M%S", time.localtime(time.time())),
                    "additional-note": ""
                }
            }

            self._m["fsa"][_name] = _fsa
            self._m["fsa-i"] = self._m["fsa-i"] + 1
            self.fsa_add(_name, False)

            return True, _name

        else:

            return False, f"FSA with same name ('{_name}') already exists, or once exists. Use a new name instead, or evoke self.clear_memory() first to remove all redundancies if there isn't a FSA with the same name in use."

    @operation
    def fsa_remove(self, name):
        """
        remove an FSA from project pool
        :param name: name of FSA to remove
        :return:
        (True, None) - fsa successfully removed
        (False, "Message") - fsa removal failed, message returned
        """
        if name not in self._m["fsa-index"]:
            return False, "There is no FSA named '" + name + "'."
        self._m["fsa-index"].remove(name)
        self.interface.fsa_removed.emit(name)
        if self._selected_fsa_name == name:
            self.fsa_select(None)

        _selected_fsa = self._m["fsa"][name]
        for node_name in _selected_fsa["node-index"]:
            for placeholder_name, ph_content in _selected_fsa["node"][node_name]["var"].items():
                if ph_content["name"]:
                    self._m["var"][ph_content["name"]]["quote"].remove(str([placeholder_name, node_name, name]))
        return True, None

    @operation
    def fsa_rename(self, new_name, **kwargs):
        """
        give an FSA a new name
        :param new_name: the new name of FSA
        :param kwargs:
        -fsa            if given, rename the given fsa; otherwise, rename the selected fsa
        :return:
        (True, None) - fsa successfully renamed
        (False, "Message") - fsa rename failed, message returned
        """
        if "fsa" in kwargs:
            old_name = kwargs["fsa"]
            if old_name not in self._m["fsa"]:
                return False, "There is no FSA named '" + old_name + "'."
        elif self._selected_fsa_name is not None:
            old_name = self._selected_fsa_name
        else:
            return False, "Please provide name of FSA, since no FSA is selected."

        if new_name in self._m["fsa"]:
            self.interface.fsa_property_change.emit(old_name, "name", old_name)
            return False, f"FSA with same name ('{new_name}') already exists, or once exists. Use a new name instead, or evoke self.clear_memory() first to remove all redundancies if there isn't a FSA with the same name in use."

        if not name_check(new_name):
            self.interface.fsa_property_change.emit(old_name, "name", old_name)
            return False, "Name must be camel case or underscore case"

        if old_name in self._m["fsa-index"]:
            self._m["fsa-index"].remove(old_name)
            self._m["fsa-index"].add(new_name)
        self._m["fsa"][new_name] = self._m["fsa"][old_name]
        self._m["fsa"][new_name]["props"]["name"] = new_name
        self._m["fsa"].pop(old_name)

        for node_name in self._m["fsa"][new_name]["node-index"]:
            node_content = self._m["fsa"][new_name]["node"][node_name]
            for ph_name, ph_content in node_content["var"].items():
                if ph_content["name"] is not None:
                    self._m["var"][ph_content["name"]]["quote"].remove(str([ph_name, node_name, old_name]))
                    self._m["var"][ph_content["name"]]["quote"].add(str([ph_name, node_name, new_name]))

        self.interface.fsa_name_change.emit(old_name, new_name)
        self.interface.fsa_property_change.emit(new_name, "name", new_name)
        return True, old_name

    def fsa_select(self, name):
        """
        set the selected fsa of the project
        :param name: name of FSA to select
        :return:
        (True, None) - fsa selected
        (False, "Message") - failed, message returned
        """
        if name is None:
            self._selected_fsa_name = None
        elif name not in self._m["fsa-index"]:
            return False, "There is no FSA named '" + name + "'."
        self._selected_fsa_name = name
        self.interface.fsa_selected.emit(name)
        return True, None

    def fsa_get_properties(self, name):
        """
        returns property of designated fsa
        :param name: name of FSA
        :return: the property dict
        """
        return copy.deepcopy(self._m["fsa"][name]["props"])

    @operation
    def fsa_set_property(self, name, key, value):
        """
        set property of selected FSA
        :param name: name of FSA
        :param key: property name
        :param value: new value of property
        :return:
        (True, Original Value) - FSA property successfully changed
        (False, "Message") - Failed changing property, message returned
        """
        if name not in self._m["fsa-index"]:
            return False, f"FSA named {name} does not exist."

        _selected_fsa = self._m["fsa"][name]

        if key == "name":
            return self.fsa_rename(value, fsa=name)
        else:
            if key in _selected_fsa["props"]:
                _original_value = _selected_fsa["props"][key]
                _selected_fsa["props"][key] = value
                self.interface.fsa_property_change.emit(name, key, value)
                return True, _original_value
            else:
                return False, f"The property '{key}' does not exist."

    def get_brand_new_records(self):
        _record_list = []
        for _records in self._m["record-index"]:
            _res, _rcd = self.record_get_properties(_records)
            if _res and not _rcd["spent"]:
                _record_list.append(_records)
        return _record_list

    def get_certain_type_var_list(self, var_type):
        return copy.deepcopy(self._m["var-sorted"][var_type])

    def get_selected_fsa_name(self):
        return self._selected_fsa_name

    def get_var_editor(self, var_name):
        var_dict = dict()
        for _var_name in self._m["var-index"]:
            var_dict[_var_name] = copy.deepcopy(self._m["var"][_var_name])
        return self._var_class[self._m["var"][var_name]["type"]].value_editor(var_name, self._m["var"][var_name]["value"], var_dict).exec()

    def __init__(self, path, **kwargs):
        """
        :param path:    string, path of project, default is none
        :param kwargs:
        -interface      an interface class, defined in core.interface
        """

        assert type(path) == str, "Path of project should be a string."

        contact = None
        if not os.path.isfile(path):
            assert "contact" in kwargs, "Every new project must have a person to contact, who is the creator or manager of the project."
            contact = kwargs.get("contact")
            assert type(contact) == str, "Contact must be a string that contains necessary information so that the project creator can be easily found."

        # project path, suffix is .sm2
        self._main_file_path = path
        self._project_dir = ""
        self._config_path = ""
        self._node_class_dir = ""

        if not self._main_file_path.endswith(".sm2"):
            self._main_file_path = self._main_file_path + ".sm2"

        self._update_path()

        # initialize project
        self._m = {
            "version": "v2",                # software version
            "file-version": "2",
            "fsa-index": set(),             # stores keys that was used in "fsa"
            "var-index": set(),             # stores list of keys that was used in "var"
            "var-sorted": dict(),
            "var-quoted": set(),

            "record-index": set(),          # stores list of records that was used in "record"

            # below are components of a typical project. From v2 on, all components are now represented as dictionaries,
            # in format of "name": {contents...}
            "fsa": {},
            "var": {},
            "record": {},

            # below are the ids to create default name of a component
            "fsa-i": 1,
            "var-i": 1,
            "record-i": 1,
        }

        # initialize configuration, its related file can be used for customized nodes / functions, and is available
        # through self.set_config() and self.get_config(). configuration file is always with project file
        self._config = {
            "name": "Untitled",             # project name, independent of file name
            "export-format": "[Time]-[Animal]",

            # the creator must leave his/her name in contact, so that if something goes wrong, people may find solutions
            "contact": contact,
            "creation-time": time.strftime("%Y%m%d-%H%M%S", time.localtime(time.time()))
        }

        # save main file and configuration; check and create node classes
        if os.path.isfile(self._main_file_path):
            self._read()
        else:
            # this is a new project, so we first check if it has nodes;
            # if it doesn't, we make a copy of "nodes" into its directory
            if not os.path.isfile(os.path.join(self._node_class_dir, "__init__.py")):
                shutil.copytree("nodes", self._node_class_dir)

            self.save()

        self.is_saved = True

        # import node classes
        self._node_class = dict()
        self.refresh_node_class()

        self._var_class = dict()
        self.refresh_variable_class()

        # interface is a class which sends signals to GUI slots, if set None, then there will be no signals
        self.interface = kwargs.get("interface", core.interface.GUIInterface(self))

        # follow is for the interface
        self.interface.resource_manager_project_renew.emit(self._config["name"], self._m)
        self.interface.resource_manager_property_renew.emit("project", self._config)
        self.interface.update_variable_create_toolbox.emit(os.path.join("variables", "icon"), self._var_class)
        self.interface.update_fsa_toolbox.emit(os.path.join(self._project_dir, "node", "icon"), self._node_class)

        _var_used = dict()
        for _var_term in self._m["var-index"]:
            _var_used[_var_term] = self._m["var"][_var_term]
        self.interface.variable_renew.emit(_var_used)

        # every element is stored in the form of a dict.
        # if the element is never quoted, it will be cleared when using self.save()

        self._selected_fsa_name = None

        # each project starts a runner
        self.runner = runner.Runner(self.interface, self)

    @operation
    def link_add(self, link_id, check_existence, fsa_name=None):
        """
        put a link in fsa link pool into use
        :param link_id: the link's registration id in fsa["link"]
        :param check_existence: whether to check if that link exists
        :param fsa_name: name of fsa, default selected fsa
        :return:
        (True, None) - link successfully added
        (False, "Message") - link addition failed, message returned
        """
        fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
        if fsa_name is None:
            return False, "FSA is not designated."
        _selected_fsa = self._m["fsa"][fsa_name]

        if check_existence:
            if link_id not in _selected_fsa["link"]:
                return False, f"Link {link_id} does not exist."

        _this_link = _selected_fsa["link"][link_id]

        if check_existence:
            if _this_link["from"] not in _selected_fsa["node-index"]:
                return False, f"The output node of target link, {_this_link['from']}, is not in use."
            if _this_link["to"] not in _selected_fsa["node-index"]:
                return False, f"The input node of target link, {_this_link['to']}, is not in use."

        if not self._node_class[_selected_fsa["node"][_this_link["to"]]["type"]].has_input:
            return False, f"Target 'to' of a link should not be a StartNode."
        if _this_link["output"] not in _selected_fsa["node"][_this_link["from"]]["out-link"]:
            return False, f"Out link '{_this_link['output']}' is not available."

        _selected_fsa["link-index"].add(link_id)
        _from_node = _selected_fsa["node"][_this_link["from"]]
        _to_node = _selected_fsa["node"][_this_link["to"]]
        _this_link["anchor"] = simple_connection(
            _from_node["x"], _from_node["y"],
            self._node_class[_from_node["type"]].out_enum[_this_link["output"]], self._node_class[_from_node["type"]].out_num,
            _to_node["x"], _to_node["y"]
        )

        _influenced_link = _from_node["out-link"][_this_link["output"]]
        if _influenced_link is not None:
            self.link_remove(_influenced_link, fsa_name)

        _from_node["out-link"][_this_link["output"]] = link_id
        _to_node["in-link"].add(link_id)

        self.interface.link_add.emit(link_id, _this_link["anchor"], fsa_name)

        return True, (link_id, _influenced_link)

    def link_get_anchor_points(self, link_id, fsa_name=None):
        if fsa_name:
            return list(self._m["fsa"][fsa_name]["link"][link_id]["anchor"])
        else:
            return list(self._m["fsa"][self._selected_fsa_name]["link"][link_id]["anchor"])

    def link_list(self, fsa_name=None):
        if fsa_name:
            return list(self._m["fsa"][fsa_name]["link-index"])
        else:
            return list(self._m["fsa"][self._selected_fsa_name]["link-index"])

    @operation
    def link_new(self, node1, output_name, node2, fsa_name=None):
        """
        link node1 with node2, with output from node1 as output_name
        :param node1: name of node1
        :param output_name: output name of node1
        :param node2: name of node2
        :param fsa_name: name of fsa, default selected fsa
        :return:
        (True, influenced link id) - if there is a link deleted because the output is previously occupied, influenced link
                                     will be the link id; other wise it's None
        (False, "Message") - Failed adding the link, message returned
        """
        fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
        if fsa_name is None:
            return False, "FSA is not designated."
        _selected_fsa = self._m["fsa"][fsa_name]

        # two nodes and output_name must exist and in use
        if node1 not in _selected_fsa["node-index"]:
            return False, f"'{node1}' is not a node in use."
        _out_link_dict = _selected_fsa["node"][node1]["out-link"]

        if node2 not in _selected_fsa["node-index"]:
            return False, f"'{node2}' is not a node in use."
        if output_name not in _out_link_dict:
            return False, f"'{output_name}' is not a legal output of '{node1}'."

        _new_link = {
            "from": node1,
            "to": node2,
            "output": output_name,
            "anchor": [[0, 0], [1, 1]]
        }
        _influenced_link = None

        _selected_fsa["link"][_selected_fsa["link-i"]] = _new_link
        _selected_fsa["link-i"] += 1
        return self.link_add(_selected_fsa["link-i"]-1, False)

    @operation
    def link_remove(self, link_id, fsa_name=None):
        """
        remove a link from selected fsa
        :param link_id: link id
        :param fsa_name: name of fsa, default selected fsa
        :return:
        (True, None) - link successfully removed
        (False, "Message") - link removal failed, message returned
        """
        fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
        if fsa_name is None:
            return False, "FSA is not designated."
        _selected_fsa = self._m["fsa"][fsa_name]
        if link_id not in _selected_fsa["link-index"]:
            return False, "requested link is not in use"

        _current_link = _selected_fsa["link"][link_id]
        _selected_fsa["node"][_current_link["from"]]["out-link"][_current_link["output"]] = None
        _selected_fsa["node"][_current_link["to"]]["in-link"].remove(link_id)
        _selected_fsa["link-index"].remove(link_id)

        self.interface.link_remove.emit(link_id, fsa_name)

        return True, None

    def var_quote_lookup(self, var_name):
        _quote = []
        if var_name in self._m["var"]:
            for str_quote in self._m["var"][var_name]["quote"]:
                _quote.append(eval(str_quote))
        return _quote

    @operation
    def node_add(self, name, check_existence, fsa_name=None, coupled_links=None):
        """
        add a node that already exists into selected FSA
        :param name: the name of node
        :param check_existence: whether to check if the variable exists in node pool of FSA
        :param fsa_name: name of fsa, default selected fsa
        :param coupled_links: links attached to the node, default will be link ids quoted in the node
        :return:
        (True, None) - node successfully added
        (False, "Message") - node addition failed, message returned
        """
        if check_existence:
            fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
            if fsa_name is None:
                return False, "FSA is not designated."
            if name not in self._m["fsa"][fsa_name]["node"]:
                return False, "There is no node named '" + name + "'."

        _selected_fsa = self._m["fsa"][fsa_name]
        if name not in _selected_fsa["node-index"]:
            _selected_fsa["node-index"].add(name)
            if not coupled_links:
                coupled_links = list(_selected_fsa["node"][name]["in-link"]) + list(_selected_fsa["node"][name]["out-link"].values())

            coupled_links = set(coupled_links)
            if None in coupled_links:
                coupled_links.remove(None)

            for link_id in coupled_links:
                self.link_add(link_id, False, fsa_name)

            for placeholder_name, ph_content in _selected_fsa["node"][name]["var"].items():
                if ph_content["name"]:
                    self._m["var"][ph_content["name"]]["quote"].add(str([placeholder_name, name, fsa_name]))
            self.interface.node_added.emit(fsa_name, name, self._m["fsa"][fsa_name]["node"][name])
            return True, None
        else:
            return False, "Node already present"

    def node_list(self, fsa_name=None):
        if fsa_name:
            return list(self._m["fsa"][fsa_name]["node-index"])
        else:
            return list(self._m["fsa"][self._selected_fsa_name]["node-index"])

    def node_get_properties(self, name, fsa_name=None):
        """
        get the value of designated property
        :param name: the name of node
        :param fsa_name: name of fsa, default selected fsa
        :return:
        (True, Value) - node property
        (False, "Message") - Failed fetching property, message returned
        """
        fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
        if fsa_name is None:
            return False, "FSA is not designated."
        _selected_fsa = self._m["fsa"][fsa_name]

        if name not in _selected_fsa["node"]:
            return False, "There is no node named '" + name + "'."

        return True, copy.deepcopy(_selected_fsa["node"][name])

    @operation
    def node_new(self, node_type, fsa_name=None, **kwargs):
        """
        create a new node in the selected FSA
        :param node_type: type of node
        :param fsa_name: name of fsa, default selected fsa
        :param kwargs:
        -name       name of the newly created node
        :return:
        (True, None) - node successfully created
        (False, "Message") - node creation failed, message returned
        """
        fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
        if fsa_name is None:
            return False, "FSA is not designated."

        if node_type not in self._node_class:
            return False, "The node type '" + node_type + "' does not exist."

        _selected_fsa = self._m["fsa"][fsa_name]
        _name = kwargs.get("name", "node" + str(_selected_fsa["node-i"]))

        if "name" not in kwargs:
            while _name in _selected_fsa["node"]:
                _selected_fsa["node-i"] += 1
                _name = "node" + str(_selected_fsa["node-i"])

        elif not loose_name_check(_name):
            return False, "Node name must be English words connected by -, _ or spacing"

        if _name not in _selected_fsa["node"]:
            _new_node = copy.deepcopy(self._node_class[node_type].template_dict)

            for key in _new_node:
                if key in kwargs:
                    _new_node[key] = copy.deepcopy(kwargs[key])

            _selected_fsa["node"][_name] = _new_node
            _selected_fsa["node-i"] += 1
            self.node_add(_name, False, fsa_name)
            return True, _name

        else:

            return False, f"Node with same name ('{_name}') already exists in this FSA, or once exists. Use a new name instead, or evoke self.clear_memory() first to remove all redundancies if there isn't a node with the same name in use."

    @operation
    def node_remove(self, name, fsa_name=None):
        """
        remove a node from selected FSA
        :param name: name of node to remove
        :param fsa_name: name of fsa, default selected fsa
        :return:
        (True, Coupled Links) - node successfully removed
        (False, "Message") - node removal failed, message returned
        """
        fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
        if fsa_name is None:
            return False, "FSA is not designated."
        _selected_fsa = self._m["fsa"][fsa_name]

        if name not in _selected_fsa["node-index"]:
            return False, "There is no node named '" + name + "'."
        _selected_fsa["node-index"].remove(name)

        _link_to_remove = set(list(_selected_fsa["node"][name]["out-link"].values()) + list(_selected_fsa["node"][name]["in-link"]))
        if None in _link_to_remove:
            _link_to_remove.remove(None)
        _link_to_remove = list(_link_to_remove)

        for link_id in _link_to_remove:
            self.link_remove(link_id, fsa_name)
        for placeholder_name, ph_content in _selected_fsa["node"][name]["var"].items():
            if ph_content["name"]:
                self._m["var"][ph_content["name"]]["quote"].remove(str([placeholder_name, name, fsa_name]))

        self.interface.node_removed.emit(fsa_name, name, _link_to_remove)

        return True, _link_to_remove

    @operation
    def node_set_property(self, name, key, value, fsa_name=None):
        """
        alter property value of a node
        :param name: node name
        :param key: the name of property to later
        :param value: new value to assign
        :param fsa_name: name of fsa, default selected fsa
        :return:
        (True, Original Value) - node property successfully changed
        (False, "Message") - Failed changing property, message returned
        """
        fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
        if fsa_name is None:
            return False, "FSA is not designated."
        _selected_fsa = self._m["fsa"][fsa_name]

        if name not in _selected_fsa["node-index"]:
            return False, "There is no node named '" + name + "'."

        if key == "name":
            if value in _selected_fsa["node"]:
                return False, f"Node with same name ('{value}') already exists, or once exists. Use a new name instead, or evoke self.clear_memory() first to remove all redundancies if there isn't a node with the same name in use."

            if not loose_name_check(value):
                return False, "Node name should be English words connected with _, - or spacing, numbers are also allowed."

            if name in _selected_fsa["node-index"]:
                _selected_fsa["node-index"].remove(name)
                _selected_fsa["node-index"].add(value)
            _selected_fsa["node"][value] = _selected_fsa["node"][name]
            _selected_fsa["node"][value]["name"] = value
            _selected_fsa["node"].pop(name)

            if _selected_fsa["node"][value]["in-link"] is not None:
                for _in_link in _selected_fsa["node"][value]["in-link"]:
                    _selected_fsa["link"][_in_link]["to"] = value

            for _out_link, _value in _selected_fsa["node"][value]["out-link"].items():
                if _value is not None:
                    _selected_fsa["link"][_value]["from"] = value

            for _ph_name in _selected_fsa["node"][value]["var"].keys():
                _var_quote = str([_ph_name, name, _selected_fsa["props"]["name"]])
                for _, _var in self._m["var"].items():
                    if _var_quote in _var["quote"]:
                        _var["quote"].remove(_var_quote)
                        _var["quote"].add(str([_ph_name, value, _selected_fsa["props"]["name"]]))

            self.interface.node_rename.emit(name, value, fsa_name)
            return True, name
        elif key == "type":
            return False, "'type' is unchangeable"
        elif key == "var":
            return False, "use 'node_set_var()' to change this property"
        elif key == "out-link" or key == "in-link":
            return False, "please use link_new(), link_add() or link_remove() to change link-related properties"
        else:
            if key in _selected_fsa["node"][name]:
                original_value = _selected_fsa["node"][name][key]
                _selected_fsa["node"][name][key] = value
                return True, original_value
            else:
                return False, "Node '" + name + "'has no property named '" + key + "'."

    @operation
    def node_set_var(self, node_name, placeholder_name, var_name, fsa_name=None):
        """
        fill variable into placeholder of designated node
        :param node_name: node's name
        :param placeholder_name: placeholder's name
        :param var_name: variable's name
        :param fsa_name: name of fsa, default selected fsa
        :return:
        (True, Original Variable) - variable successfully set into the node
        (False, "Message") - Failed setting the variable, message returned
        """
        fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
        if fsa_name is None:
            return False, "FSA is not designated."
        _selected_fsa = self._m["fsa"][fsa_name]
        if node_name not in _selected_fsa["node-index"]:
            return False, f"There is no node named '{node_name}'."
        if placeholder_name not in _selected_fsa["node"][node_name]["var"]:
            return False, f"Node '{node_name}' does not have a placeholder named '{placeholder_name}'."
        _original_variable_name = _selected_fsa["node"][node_name]["var"][placeholder_name]["name"]

        if var_name:
            if var_name not in self._m["var"]:
                return False, f"There is no variable named '{var_name}'."

            if self._m["var"][var_name]["type"] != _selected_fsa["node"][node_name]["var"][placeholder_name]["type"]:
                return False, f"Variable {var_name}'s type is {self._m['var'][var_name]['type']}, which does not match the placeholder's requirement ({_selected_fsa['node'][node_name]['var'][placeholder_name]['type']})."

        # if there is previously a variable in placeholder, it should be removed first
        if _original_variable_name:
            _selected_fsa["node"][node_name]["var"][placeholder_name]["name"] = None
            if str([placeholder_name, node_name, fsa_name]) in self._m["var"][_original_variable_name]["quote"]:
                self._m["var"][_original_variable_name]["quote"].remove(str([placeholder_name, node_name, fsa_name]))
            if not self._m["var"][_original_variable_name]["quote"]:
                self._m["var-quoted"].remove(_original_variable_name)
        else:
            _original_variable_name = ""

        if var_name:
            _selected_fsa["node"][node_name]["var"][placeholder_name]["name"] = var_name
            self._m["var-quoted"].add(var_name)
            self._m["var"][var_name]["quote"].add(str([placeholder_name, node_name, fsa_name]))
        else:
            var_name = ""

        self.interface.ph_set_var.emit(node_name, placeholder_name, var_name, fsa_name)

        return True, _original_variable_name

    @operation
    def note_add(self, note_id, check_existence, fsa_name=None):
        """
        add a record that already exists into project pool
        :param note_id: the name of record
        :param check_existence: whether to check if the record exists in _m
        :param fsa_name: name of fsa, default selected fsa
        :return:
        (True, None) - record successfully added
        (False, "Message") - record addition failed, message returned
        """
        fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
        if fsa_name is None:
            return False, "FSA is not designated."
        _selected_fsa = self._m["fsa"][fsa_name]

        if check_existence:
            if note_id not in _selected_fsa["note"]:
                return False, "There is no note whose id is '" + note_id + "'."
        if note_id not in _selected_fsa["note-index"]:
            _selected_fsa["note-index"].add(note_id)
            return True, None
        else:
            return False, "Note already present"

    def note_get_properties(self, note_id):
        """
        get the value of all note properties
        :param note_id: note ID
        :return:
        (True, Value) - variable property
        (False, "Message") - Failed fetching property, message returned
        """

        if self._selected_fsa_name is None:
            return False, "FSA is not designated."

        _selected_fsa = self._m["fsa"][self._selected_fsa_name]

        if note_id in _selected_fsa["note-index"]:
            return True, copy.deepcopy(_selected_fsa["note"][note_id])
        else:
            return False, f"There isn't a note whose id is {note_id} in use."

    @operation
    def note_new(self, fsa_name=None, **kwargs):
        """
        create a new note in designated FSA
        :param fsa_name: name of fsa, default selected fsa
        :param kwargs:
        :return:
        (True, None) - note successfully created
        (False, "Message") - note creation failed, message returned
        """
        fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
        if fsa_name is None:
            return False, "FSA is not designated."
        _selected_fsa = self._m["fsa"][fsa_name]

        _new_note = {
            "x": kwargs.get("x", 0),
            "y": kwargs.get("y", 0),
            "w": kwargs.get("w", 0),
            "h": kwargs.get("h", 0),
            "note": ""
        }

        _selected_fsa["note"][_selected_fsa["note-i"]] = _new_note
        self.note_add(_selected_fsa["note-i"], False)
        _selected_fsa["note-i"] += 1
        return True, None

    @operation
    def note_remove(self, note_id, fsa_name=None):
        """
        remove a note from designated FSA
        :param note_id: ID of note
        :param fsa_name: name of fsa, default selected fsa
        :return:
        (True, None) - note successfully removed
        (False, "Message") - note removal failed, message returned
        """
        fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
        if fsa_name is None:
            return False, "FSA is not designated."
        _selected_fsa = self._m["fsa"][fsa_name]

        if note_id in _selected_fsa["note-index"]:
            _selected_fsa["note-index"].remove(note_id)
            return True, None
        else:
            return False, f"There isn't a note whose id is {note_id} in use."

    @operation
    def note_set_property(self, note_id, key, value, fsa_name=None):
        """
        Set property of a note
        :param note_id: note ID
        :param key: name of the property to set
        :param value: the value to set
        :param fsa_name: name of fsa, default selected fsa
        :return:
        (True, Original Value) - variable property successfully changed
        (False, "Message") - Failed changing property, message returned
        """
        fsa_name = self._selected_fsa_name if fsa_name is None else fsa_name
        if fsa_name is None:
            return False, "FSA is not designated."
        _selected_fsa = self._m["fsa"][fsa_name]

        if note_id in _selected_fsa["note-index"]:
            if key in _selected_fsa["note"][note_id]:
                _original_value = _selected_fsa["note"][note_id][key]
                _selected_fsa["note"][note_id][key] = value
                return True, _original_value
            else:
                return False, f"Property named '{key}' does not exist."
        else:
            return False, f"There isn't a note whose id is {note_id} in use."

    def _read(self):

        # main file
        with open(self._main_file_path, 'rb') as f:
            self._m = pickle.load(f)

        # configuration file
        with open(self._config_path, 'rb') as f:
            self._config = pickle.load(f)

    @operation
    def project_property_set(self, key, value):
        if key == "name":
            _original_name = self._config[key]
            self._config[key] = value
            self.interface.project_name_change.emit(value)
            self.interface.project_property_change.emit("name", value)
            return True, _original_name
        else:
            if key in self._config:
                _original_value = self._config[key]
                self._config[key] = value
                self.interface.project_property_change.emit(key, value)
                return True, _original_value
            else:
                return False, f"Key '{key}' does not exist."

    def project_properties_get(self):
        """
        :return: a copy of project basic properties
        """
        return copy.deepcopy(self._config)

    @operation
    def record_add(self, name, check_existence=True):
        """
        add a record that already exists into project pool
        :param name: the name of record
        :param check_existence: whether to check if the record exists in _m
        :return:
        (True, None) - record successfully added
        (False, "Message") - record addition failed, message returned
        """
        if check_existence:
            if name not in self._m["record"]:
                return False, "There is no record named '" + name + "'."
        if name not in self._m["record-index"]:
            self._m["record-index"].add(name)
            self.interface.record_added.emit(name)
            self.interface.record_selected.emit(name)
            return True, name
        else:
            return False, "Record already present"

    def record_get_path(self, name):
        """
        get the path of certain record
        note: this path may not exist.
        :param name: the name of the record
        :return:
        (True, Value) - variable property
        (False, "Message") - Failed fetching property, message returned
        """
        if name not in self._m["record-index"]:
            return False, "Record does not exist"

        return True, (os.path.join(self._m["record"][name]["path"], name + ".smrprop"),
                      os.path.join(self._m["record"][name]["path"], name + ".smrdata"))

    def record_get_properties(self, name):
        """
        get the value of all record properties
        :param name: the name of the record
        :return:
        (True, Value) - variable property
        (False, "Message") - Failed fetching property, message returned
        """
        if name not in self._m["record-index"]:
            return False, "Record does not exist"

        _prop_file_name = os.path.join(self._m["record"][name]["path"], name + ".smrprop")
        if os.path.isfile(_prop_file_name):
            with open(_prop_file_name, 'rb') as f:
                _property = pickle.load(f)
        else:
            return False, "Record file does not exist, may have been renamed, moved or deleted. Open record browser to check and fix."

        return True, copy.deepcopy(_property)

    def record_list(self):
        """
        list all variables in use
        :return: all names of variables in use
        """
        return list(self._m["record-index"])

    @operation
    def record_load(self, _path):
        if os.path.isfile(_path) and os.path.splitext(_path)[-1] == ".smrprop":
            with open(_path, 'rb') as f:
                _property = pickle.load(f)
            _rcd = {
                "name": _property["name"],
                "path": _property["main-path"],
                "fsa": None
            }

            if _rcd["name"] not in self._m["record"]:
                self._m["record"][_rcd["name"]] = _rcd
                self.record_add(_rcd["name"], False)
                return True, _rcd["name"]
            else:
                return False, "Record load failed: name conflict."
        else:
            return False, "File does not exist or not a .smrprop file."

    def record_content_load(self, name):
        if name not in self._m["record-index"]:
            return False, "Record does not exist"

        _prop_file_name = os.path.join(self._m["record"][name]["path"], name + ".smrdata")

        if os.path.isfile(_prop_file_name):

            with open(_prop_file_name, 'rb') as f:
                _content = pickle.load(f)

        else:
            _content = None

        return True, _content

    @operation
    def record_new(self, _path, **kwargs):
        """
        create a new record
        :param _path: the directory (not file name!) to save the record
        :param kwargs:
        -name           name of record, default is record+"record_i"
        :return:
        (True, None) - record successfully created
        (False, "Message") - record creation failed, message returned
        """
        _name = kwargs.get("name", "record" + str(self._m["record-i"]))

        if "name" not in kwargs:
            while _name in self._m["record"]:
                self._m["record-i"] += 1
                _name = "record" + str(self._m["record-i"])

        elif not name_check(_name):
            return False, "Name must be camel case or underscore case"

        if _name not in self._m["record"]:

            _rcd = {
                "name": _name,
                "fsa": None,
                "experimenter": kwargs.get("experimenter", ""),
                "subject": kwargs.get("subject", ""),
                "round": kwargs.get("round", ""),
                "trial": kwargs.get("trial", ""),
                "session": kwargs.get("session", ""),
                "block": kwargs.get("block", ""),
                "group": kwargs.get("group", ""),
                "creation-datetime": time.strftime("%Y%m%d-%H%M%S", time.localtime(time.time())),
                "record-datetime": 0,
                "spent": False,                           # record can only be used by a runner when it is not spent
                "note": "",                               # experimenter notes
                "length": 0,
                "main-path": _path,
                "sub-path": kwargs.get("subPath", [])     # a list holding other possible data from possible software, such as OpenEphys or Unity VR
            }

            # content part will be written once, when the record is recorded
            _rcd_path = os.path.join(_path, _name + ".smrprop")
            if not os.path.isdir(_path):
                os.mkdir(_path)

            with open(_rcd_path, "wb") as f:
                pickle.dump(_rcd, f)

            self._m["record"][_name] = {
                "name": _name,
                "path": _path,
                "fsa": self._selected_fsa_name
            }
            self.record_add(_name, False)
            self._m["record-i"] += 1

            return True, _name
        else:
            return False, f"Record with same name ('{_name}') already exists, or once exists. Use a new name instead, or clear project memories to remove redundancies if there isn't a record with the same name in use (Warning: SmartMice may overwrite previously discarded records)."

    @operation
    def record_remove(self, name):
        """
        remove a record from project pool. note: the record file will not be deleted.
        :param name: name of record to remove
        :return:
        (True, None) - record successfully removed
        (False, "Message") - record removal failed, message returned
        """
        if name not in self._m["record-index"]:
            return False, "Record does not exist"

        self._m["record-index"].remove(name)
        self.interface.record_removed.emit(name)
        self.fsa_select(None)
        return True, None

    @operation
    def record_set_property(self, name, key, value):
        """
        alter property value of a record
        :param name: record name
        :param key: the name of property to later
        :param value: new value to assign
        :return:
        (True, Original Value) - record property successfully changed
        (False, "Message") - Failed changing property, message returned
        """
        if name not in self._m["record-index"]:
            return False, "Record does not exist"

        _prop_file_name = os.path.join(self._m["record"][name]["path"], name + ".smrprop")
        with open(_prop_file_name, 'rb') as f:
            _property = pickle.load(f)

        if key not in _property:
            return False, f"Property name {key} does not exist."

        if key == "spent":
            return False, "Property 'spent' cannot be altered."

        elif key == "name":
            if value in self._m["record"]:
                self.interface.record_property_change.emit(name, "name", name)
                return False, f"Record with same name ('{value}') already exists, or once exists. Use a new name instead, or clear project memories to remove redundancies if there isn't a record with the same name in use (Warning: SmartMice may overwrite previously discarded records)."

            if not loose_name_check(value):
                self.interface.record_property_change.emit(name, "name", name)
                return False, "Node name should be English words connected with _, - or spacing, numbers are also allowed."

            if name in self._m["record-index"]:
                self._m["record-index"].remove(name)
                self._m["record-index"].add(value)
            self._m["record"][value] = self._m["record"][name]
            _prop_file_name = os.path.join(self._m["record"][value]["path"], value + ".smrprop")
            os.rename(os.path.join(self._m["record"][value]["path"], name + ".smrprop"), _prop_file_name)
            self._m["record"][value]["path"] = os.path.dirname(_prop_file_name)
            _data_path = os.path.join(self._m["record"][value]["path"], name + ".smrdata")
            _new_data_path = os.path.join(self._m["record"][value]["path"], value + ".smrdata")
            if os.path.isfile(_data_path):
                os.rename(_data_path, _new_data_path)
            _property["main-path"] = os.path.dirname(_new_data_path)
            self._m["record"][value]["name"] = value
            self._m["record"].pop(name)
            self.interface.record_name_change.emit(name, value)

        _prev_value = _property[key]
        _property[key] = value
        if key == "name":
            self.interface.record_property_change.emit(value, key, value)
            self.save()
        else:
            self.interface.record_property_change.emit(name, key, value)

        with open(_prop_file_name, 'wb') as f:
            pickle.dump(_property, f)

        return True, _prev_value

    # noinspection PyUnresolvedReferences
    def refresh_node_class(self):
        # pop previously loaded node classes
        sys.path.append(self._project_dir)

        # python is not real language, its module importing sucks
        if "node" in sys.modules:
            del sys.modules["node"]

        node = importlib.import_module("node")

        self._node_class = node.NODE_CLASS_DICT
        sys.path.remove(self._project_dir)

    # noinspection PyUnresolvedReferences
    def refresh_variable_class(self):
        if "variables" in sys.modules:
            del sys.modules["variables"]

        variables = importlib.import_module("variables")
        self._var_class = variables.VAR_CLASS_DICT

        for _ele in self._var_class:
            if _ele not in self._m["var-sorted"]:
                self._m["var-sorted"][_ele] = set()

    def run(self, record_name):
        if self._selected_fsa_name is None:
            return False, "FSA is not designated."

        _selected_fsa = self._m["fsa"][self._selected_fsa_name]

        if record_name in self._m["record"]:
            _res, _rcd = self.record_get_properties(record_name)

            if not _res:
                return False, f"Cannot match file for Record {record_name}. Open record browser to fix."

            if _rcd["spent"]:
                return False, f"Record {record_name} is spent, and should not be used twice."

            self.save()
            _compile_state, _compile_info = self.runner.fsa_compile(_selected_fsa, self._m["var"], self._node_class, self._var_class)
            if _compile_state:
                self._m["record"][record_name]["fsa"] = self._selected_fsa_name
                self.record_set_property(record_name, "fsa", self._selected_fsa_name)
                _run_state, _run_message = self.runner.run(self._m["record"][record_name], _compile_info)
                if _run_state:
                    return True, None
                else:
                    return _run_state, _run_message
            else:
                return False, "Compile error: " + str(_compile_info)
        else:
            return False, f"Record {record_name} does not exist."

    def save(self, **kwargs):

        # when another path different from current one is designated,
        # we first make a copy of node classes to new directory, then continue saving
        path_arg = kwargs.get("path", None)
        if path_arg is not None:
            if not os.path.samefile(self._main_file_path, path_arg):
                node_class_dir_prev = self._node_class_dir
                self._main_file_path = path_arg
                self._update_path()

                if not os.path.isfile(os.path.join(self._node_class_dir, "__init__.py")):
                    shutil.copytree(node_class_dir_prev, self._node_class_dir)

        # main file
        # do this in other cases
        # self.clear_memory()

        with open(self._main_file_path, 'wb') as f:
            pickle.dump(self._m, f)

        # configuration file
        with open(self._config_path, 'wb') as f:
            pickle.dump(self._config, f)

        self.is_saved = True

    def _update_path(self):

        # we update following paths, based on main file path
        self._project_dir = os.path.dirname(os.path.abspath(self._main_file_path))
        self._config_path = os.path.join(self._project_dir, "config.smc")
        self._node_class_dir = os.path.join(self._project_dir, "node")

    @operation
    def var_add(self, name, check_existence=True):
        """
        add a variable that already exists into project pool
        :param name: the name of variable
        :param check_existence: whether to check if the variable exists in _m
        :return:
        (True, None) - variable successfully added
        (False, "Message") - variable addition failed, message returned
        """
        if check_existence:
            if name not in self._m["var"]:
                return False, "There is no variable named '" + name + "'."
        if name not in self._m["var-index"]:
            self._m["var-index"].add(name)
            self._m["var-sorted"][self._m["var"][name]["type"]].add(name)
            self.interface.var_added.emit(self._m["var"][name]["type"], name)
            return True, None
        else:
            return False, "Variable already present"

    def var_get_properties(self, name):
        """
        get the value of a variable's property
        :param name: the name of the variable
        :return:
        (True, Value) - variable property
        (False, "Message") - Failed fetching property, message returned
        """
        if name not in self._m["var"]:
            return False, "There is no variable named '" + name + "'."

        return True, copy.deepcopy(self._m["var"][name])

    def var_list(self):
        """
        list all variables in use
        :return: all names of variables in use
        """
        return list(self._m["var-index"])

    @operation
    def var_new(self, var_type, **kwargs):
        """
        create a new variable
        :param var_type       "MInt", "MStr", "MFloat" or other acceptable variable types
        :param kwargs:
        -name           name of variable, default is var+"var_index"
        :return:
        (True, None) - variable successfully created
        (False, "Message") - variable creation failed, message returned
        """

        if var_type not in self._var_class:
            return False, "Required variable type does not exist"

        _name = kwargs.get("name", "Var" + str(self._m["var-i"]))

        if "name" not in kwargs:
            while _name in self._m["var"]:
                self._m["var-i"] += 1
                _name = "Var" + str(self._m["var-i"])

        elif not name_check(_name):
            return False, "Name must be camel case or underscore case"

        if _name not in self._m["var"]:

            # we first fetch a template dictionary from the variable class, then copy all input to this template
            _var = copy.deepcopy(self._var_class[var_type].template_dict)

            for key in _var:
                if key in kwargs:
                    _var[key] = copy.deepcopy(kwargs[key])

            self._m["var"][_name] = _var
            self._m["var-i"] += 1
            self.var_add(_name, False)

            return True, _name

        else:

            return False, f"Variable with same name ('{_name}') already exists, or once exists. Use a new name instead, or clear project memories first to remove all redundancies if there isn't a variable with the same name in use."

    @operation
    def var_remove(self, name):
        """
        remove a variable from project pool
        :param name: name of variable to remove
        :return:
        (True, None) - variable successfully removed
        (False, "Message") - variable removal failed, message returned
        """
        if name not in self._m["var-index"]:
            return False, "There is no variable named '" + name + "'."
        if name in self._m["var-quoted"]:
            return False, f"Variable {name} has been quoted, thus cannot be deleted. This is a protection in case you mis-manipulated. If that quotation does not exist anymore, you can clear project memories to precede."

        self._m["var-index"].remove(name)
        self._m["var-sorted"][self._m["var"][name]["type"]].remove(name)
        self.interface.var_removed.emit(name)
        return True, None

    @operation
    def var_set_property(self, name, key, value):
        """
        alter property value of a variable
        :param name: variable name
        :param key: the name of property to later
        :param value: new value to assign
        :return:
        (True, Original Value) - variable property successfully changed
        (False, "Message") - Failed changing property, message returned
        """
        if name not in self._m["var"]:
            return False, "There is no variable named '" + name + "'."

        if key == "value":
            try:
                value = self._var_class[self._m["var"][name]["type"]].filter_func(value)
            except ValueError as e:
                self.interface.var_property_change.emit(name, key, str(self._m["var"][name][key]))
                return False, e.args

        if key == "name":
            if value in self._m["var"]:
                self.interface.var_property_change.emit(name, key, name)
                return False, f"Variable with same name ('{value}') already exists, or once exists. Use a new name instead, or evoke self.clear_memory() first to remove all redundancies if there isn't a variable with the same name in use."

            if not name_check(value):
                self.interface.var_property_change.emit(name, key, name)
                return False, "Name must be camel case or underscore case"

            if name in self._m["var-index"]:
                _var_type = self._m["var"][name]["type"]
                self._m["var-index"].remove(name)
                self._m["var-sorted"][_var_type].remove(name)
                self._m["var-index"].add(value)
                self._m["var-sorted"][_var_type].add(value)
            self._m["var"][value] = self._m["var"][name]
            self._m["var"][value]["name"] = value
            self._m["var"].pop(name)

            for _var_quote in self.var_quote_lookup(value):
                self._m["fsa"][_var_quote[2]]["node"][_var_quote[1]]["var"][_var_quote[0]]["name"] = value

            if name in self._m["var-quoted"]:
                self._m["var-quoted"].remove(name)
                self._m["var-quoted"].add(value)

            self.interface.var_renamed.emit(name, value)
            self.interface.var_property_change.emit(value, "name", value)
            return True, name
        elif key != "type":
            if key in self._m["var"][name]:
                original_value = self._m["var"][name][key]
                self._m["var"][name][key] = value
                self.interface.var_property_change.emit(name, key, str(value))
                return True, original_value
            else:
                return False, "Variable '" + name + "'has no property named '" + key + "'."
        else:
            return False, "'type' is unchangeable"
