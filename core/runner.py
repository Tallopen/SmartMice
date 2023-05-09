import threading
import time
from PyQt6.QtCore import QThread

import core.record as record


class MyThread(QThread):

    def __init__(self, target, args):
        super(QThread, self).__init__()
        self._foo = target
        self.args = args

    def run(self):
        self._foo(*self.args)


class Runner:

    def __init__(self, interface, gui_main):
        self._compiled = False
        self._entrance = None
        self._interface = interface
        self.guiMain = gui_main
        self._record = None
        self._is_running = False
        self._is_pausing = False
        self._start_time = 0
        self._t1 = None

    def fsa_compile(self, fsa, variable_dict, node_class, var_class):

        _compiled_nodes = dict()
        _compiled_variables = dict()
        _quoted_variables = list()

        for _node_name, _node in fsa['node'].items():
            if _node_name in fsa['node-index']:
                for _ph_name, _v in _node['var'].items():
                    if _v['name']:
                        _quoted_variables.append(_v['name'])
                        if variable_dict[_v['name']]['type'] == "MVarArray" or variable_dict[_v['name']]['type'] == "MNaiveDisplay":
                            _quoted_variables.extend(list(variable_dict[_v['name']]['value']))
                        elif variable_dict[_v['name']]['type'] == "MTracker":
                            if variable_dict[_v['name']]['value']["cam"]:
                                _quoted_variables.append(variable_dict[_v['name']]['value']["cam"])
                    else:
                        return False, f"Unfilled placeholder '{_ph_name}' detected in node '{_node_name}'."

        _quoted_variables = list(set(_quoted_variables))

        for _var_name in _quoted_variables:
            _compiled_variables[_var_name] = var_class[variable_dict[_var_name]['type']](
                variable_dict[_var_name]['value'], _var_name
            )

        for _, _variable in _compiled_variables.items():
            if _variable.requirements['variable']:
                _variable.variable = _compiled_variables
            if _variable.requirements['runner']:
                _variable.runner = self
            if _variable.requirements['interface']:
                _variable.interface = self._interface

        _start_nodes = []
        _end_nodes = []

        for _node_name in fsa['node-index']:
            _var_dict = dict()
            for _ph_name, _var_term in fsa['node'][_node_name]['var'].items():
                if _var_term['name'] is None:
                    return False, f"There is a vacant placeholder '{_ph_name}' in node '{_node_name}'."
                _var_dict[_ph_name] = _compiled_variables[_var_term['name']]
            try:
                _compiled_nodes[_node_name] = node_class[fsa['node'][_node_name]['type']](runtime_dict={
                    'var': _var_dict,
                    'name': _node_name
                })
            except Exception as e:
                return False, f"Error at node {_node_name}: {e.args}"
            if not node_class[fsa['node'][_node_name]['type']].has_input:
                _start_nodes.append(_compiled_nodes[_node_name])
            if fsa['node'][_node_name]['type'] == 'EndNode':
                _end_nodes.append(_compiled_nodes[_node_name])

        if len(_start_nodes) != 1:
            return False, f'There should be 1 start nodes in one FSA; found {len(_start_nodes)}.'

        if not len(_end_nodes):
            return False, 'There should be at least 1 end nodes in one FSA.'

        for _node_name in fsa['node-index']:
            _link_jump = dict()
            for _key, _link_id in fsa['node'][_node_name]['out-link'].items():
                if _link_id is None:
                    return False, f"Unlinked output '{_key}' detected in node '{_node_name}'."
                _link_jump[_key] = _compiled_nodes[fsa['link'][_link_id]['to']]
            _compiled_nodes[_node_name].runtime['jump'] = _link_jump

        self._entrance = _start_nodes
        self._compiled = True
        return True, _compiled_variables

    def _run_func(self, _record):

        _erroneous = False
        _error_message = ''
        self._interface.run_begin.emit()
        self._is_running = True
        _current_node = self._entrance[0]
        _current_node_name = self._entrance[0].runtime['name']
        _output = None

        threading.Thread(target=self._tic).start()

        try:
            self._start_time = time.time()
            _record.set_start_time(self._start_time)
            _record.log('System Event', 'Start Running', str(self._start_time))

            while self._is_running:
                if self._is_pausing:
                    time.sleep(0.1)
                else:
                    self._interface.run_evoke.emit(_current_node.runtime['name'])
                    _output = _current_node.run(_record)
                    if _output is None:
                        self._is_running = False
                    else:
                        _current_node = _output
                        _current_node_name = _current_node.runtime['name']

            _record.log('System Event', 'Running Ends', '')
            _record.time_length = time.time() - self._start_time
            _record.save()

            self._is_running = False
            self._interface.run_end.emit()

            return True, None

        except Exception as e:
            _erroneous = True
            _error_message = e.args[0]
            self._is_running = False
            _record.log('System Event', 'Error Encountered', f"Error at '{_current_node_name}': \nERROR MESSAGE: {_error_message}\nRunning aborted.")
            _record.save()
            self._interface.run_end.emit()
            return False, f"Error at '{_current_node_name}': \nERROR MESSAGE: {_error_message}\nRunning aborted."

    def run(self, record_dict, _compiled_variables):
        """
        run the compiled FSA
        :param record_dict: the dictionary of designated record
        :param _compiled_variables: what was returned in self.compile()
        :return:
        (True, None) - run successful
        (False, "Message") - error encountered, message returned
        """
        if not self._is_running:
            if self._compiled:
                self._record = record.Record(self._interface, record_dict)
                for _variable in _compiled_variables.values():
                    _variable.set_record(self._record)
                else:
                    self._t1 = MyThread(target=self._run_func, args=(self._record,))
                    self._t1.start()
                    return True, None

            return False, 'No FSA is compiled.'
        else:
            return False, 'There is currently a program running.'

    def time(self):
        return time.time() - self._start_time

    def _tic(self):
        while self._is_running:
            self._interface.tick.emit(time.time() - self._start_time)
            time.sleep(0.05)

    def pause(self):
        if self._is_running:
            self._is_pausing = True
            self._record.log('System Event', 'Pause', '')

    def continue_run(self):
        if self._is_running:
            self._is_pausing = False
            self._record.log('System Event', 'Continue', '')

    def is_running(self):
        return self._is_running
