# -*- coding: utf-8 -*-
# created at: 2022/9/14 9:14
# author    : Gao Kai
# Email     : gaosimin1@163.com

import copy
import os.path
import pickle
import time


class Record:

    def __init__(self, interface, record_dict):

        self._info = []
        self._interface = interface
        self._param = record_dict
        self.time_length = 0
        self._start_time = 0
        self._data_accessory = []

        self._runner_thread = None

    def log(self, _type, name, value):
        _t = time.time()
        _log = [round(_t - self._start_time, 4), _type, name, value]
        self._info.append(_log)
        self._interface.record_logged.emit(_log)

    def get_time(self):
        return round(time.time() - self._start_time, 4)

    def append_data_accessory(self, _type, _value):
        self._data_accessory.append((_type, _value))

    def save(self):
        _data_file_path = os.path.join(self._param["path"], self._param["name"] + '.smrdata')
        _prop_file_path = os.path.join(self._param["path"], self._param["name"] + '.smrprop')
        with open(_data_file_path, 'wb') as f:
            pickle.dump({
                "record": self._info
            }, f)
        with open(_prop_file_path, 'rb') as f:
            _props = pickle.load(f)
        _props["length"] = self.time_length
        _props["record-datetime"] = time.strftime("%Y%m%d-%H%M%S", time.localtime(self._start_time))
        _props["spent"] = True
        _props["sub-path"] = copy.deepcopy(self._data_accessory)
        with open(_prop_file_path, 'wb') as f:
            pickle.dump(_props, f)

    def set_start_time(self, _time):
        self._start_time = _time

    def get_a_parent(self):
        return self._interface.guiMain

    def set_runner_thread(self, runner_thread):
        self._runner_thread = runner_thread

    def get_runner_thread(self):
        return self._runner_thread
