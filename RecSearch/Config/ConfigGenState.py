from RecSearch.Config.ConfigGenMeta import meta_data_objects
from RecSearch.Config.ConfigGenKeyManage import default_key_manager, KeyManager
from RecSearch.Config.ConfigGenValidate import InputValidator
from RecSearch.ExperimentSupport.ExperimentParameters import ExperimentParameters
import PySimpleGUI as sg
from copy import deepcopy
from configobj import ConfigObj
import pandas as pd
from os.path import normpath


class MainData:
    """Store main data information"""
    def __init__(self, datafile: str = '', dataconfig: dict = None):
        if datafile:
            self.datafile = datafile
            self.columns = list(pd.read_csv(self.datafile, nrows=0))
            self.use_columns = []
            self.index_columns = []
            # AST = Abstract Syntax Tree used for converting str to List/Dict
            self.ast_columns = []
        elif dataconfig:
            self.datafile = normpath(dataconfig['datafile'])
            self.columns = list(pd.read_csv(self.datafile, nrows=0))
            self.use_columns = dataconfig['use_columns']
            self.index_columns = dataconfig['index_columns']
            self.ast_columns = dataconfig['ast_columns']
        else:
            raise NotImplementedError

    def finish(self, use_columns: list, index_columns: list, ast_columns: list, datafile: str):
        """Finish configuring Data, set state"""
        self.use_columns = use_columns
        self.index_columns = index_columns
        self.ast_columns = ast_columns
        self.datafile = datafile

    def get_columns(self):
        """Get the stored column names from this"""
        return self.columns

    def get_ast_columns(self):
        return self.ast_columns

    def get_use_columns(self):
        return self.use_columns

    def get_index(self):
        return self.index_columns

    def get_datafile(self):
        return self.datafile

    def dump(self):
        """Get the state as a dictionary"""
        output = {'datafile': self.datafile}
        for attr in dir(self):
            if attr.endswith('_columns') and not callable(value := getattr(self, attr)):
                output[attr] = value
        return output


class Loader:
    def __init__(self, configfile: str):
        self.ExpPar = ExperimentParameters(configfile, alternative=True)
        self.cfg = self.ExpPar.cfg()
        self.cfg.pop('DATA')

    def get_loaded_cfg(self):
        return self.cfg


class MainDataWorkerStateManager:
    """Manages state for all DataWorkers"""
    def __init__(self):
        self.meta_dw, __ = meta_data_objects()
        self.key_manager = default_key_manager
        for name in self.meta_dw.get_dataworkers():
            setattr(self, name, MainDataWorkerState(name, getattr(self.key_manager, name)))

    def load(self, configfile: str):
        loader = Loader(configfile)
        for name, configs in loader.get_loaded_cfg().items():
            getattr(self, name).load_state(configs)

    def reset_state(self):
        for name in self.meta_dw.get_dataworkers():
            getattr(self, name).reset_state()



class MainDataWorkerState:
    """Manages state for its DataWorker"""
    def __init__(self, data_worker: str, key_manager: KeyManager):
        self.dw = data_worker
        self.di = ''
        self.key_manager = key_manager
        self.converter = StateConverter(self.dw, self.key_manager)
        self.meta_dw, __ = meta_data_objects()
        self.validator = InputValidator()
        self.state = []
        self.view_index = 0
        self.current = {}
        self.persist_interface_state = False
        self.updated_state = False

    def reset_state(self):
        self.current = {}
        self.view_index = 0
        self.state = []

    def get_updated_state(self):
        return_value = self.updated_state
        self.updated_state = False
        return return_value

    def load_state(self, configs: dict):
        self.state = []
        for name, config in configs.items():
            if isinstance(config, dict):
                config.pop('name')
                self.state.append('\n'.join(ConfigObj({name: config}).write()))
        self.view_index = 1

    def dump(self):
        """Get full state"""
        return self.state

    def set_interface(self, interface: str):
        """Set the DataWorker's interface"""
        self.di = interface

    def get_di(self):
        """Get the DataWorker's interface"""
        return self.di

    def edit(self, window, values):
        """Grab the current DataWorker in view state and populate GUI with its values for editing"""
        if self.view_index:
            self.current = {}
            for key, value in self.converter.view_to_key(self.state[self.view_index-1]).items():
                method_key = self.key_manager.get_method_key(self.dw)
                if key in values.keys():
                    if type(window[key]) in [sg.Input, sg.Combo]:
                        window[key].update(value=value)
                    elif type(window[key]) in [sg.Listbox]:
                        window[key].update(values=value)
                else:
                    self.current[key] = value

                if key == method_key:
                    self.set_interface(value)
            self.persist_interface_state = True

    def get_view_state(self):
        """Get the state of the currently viewed configuration"""
        if self.view_index:
            return self.state[self.view_index - 1]
        else:
            return ''

    def idx(self):
        """Get the current view index"""
        return self.view_index

    def get_current(self):
        """Get the current state"""
        return self.current

    def get_persist(self):
        """Get if interface state has not been to added yet to allow editing after popup closed"""
        return self.persist_interface_state

    def get_parameter(self, name: str, parameter: str, is_list: bool = False):
        """Get a specific parameter for a configuration"""
        for state in self.state:
            split_state = state.split('\n')
            # Get Name from [Name]
            if split_state[0][1:-1] == name:
                split_values, = [line.split('= ')[1] for line in split_state if line.strip().startswith(parameter)]
                if is_list:
                    return split_values.split(', ')
                else:
                    return split_values
        return None

    def get_names(self):
        """Get the names of all configurations for this DataWorker state"""
        return [s.split('\n')[0][1:-1] for s in self.state]

    def beginning(self):
        """Set the view index to the beginning for << button"""
        if self.view_index:
            self.view_index = 1

    def ending(self):
        """Set the view index to the end for >> button"""
        if self.view_index:
            self.view_index = self.end()

    def end(self):
        """Get the length of state for viewing"""
        return len(self.state)

    def increment(self):
        """Increment the view index for > button"""
        if self.view_index < self.end():
            self.view_index += 1
        elif self.view_index and self.view_index == self.end():
            self.view_index = 1

    def decrement(self):
        """Decrement the view index for < button"""
        if self.view_index > 1:
            self.view_index -= 1
        elif self.view_index == 1:
            self.view_index = self.end()

    def change_method(self, interface: str):
        """Update state for changing interface method"""
        for key in self.key_manager.get_all_interface_keys(self.dw, self.di):
            self.current.pop(key, None)
        self.persist_interface_state = False
        self.di = interface

    def persist(self, sub_values: dict):
        """Persist interface settings until change method or submit"""
        self.current.update({k: v for k,v in sub_values.items() if k in self.key_manager.get_all_interface_keys(self.dw, self.di)})
        self.persist_interface_state = True

    def message(self):
        """Get current view index of total view length"""
        return str(self.view_index) + ' / ' + str(self.end())

    def reset(self, window):
        """Reset the GUI after submitting configuration"""
        for key in set(self.current.keys()).union(set(self.key_manager.get_all_worker_keys(self.dw))):
            if ':Worker:' in key:
                default = self.validator.get_default(key)
                window[key].update(value=default)
        self.current = {}
        self.di = ''
        self.persist_interface_state = False

    def remove(self):
        """Remove the currently viewed configuration from state"""
        if self.end():
            if self.view_index == self.end():
                self.state.pop(self.view_index - 1)
                self.view_index -= 1
            else:
                self.state.pop(self.view_index - 1)
        if not self.end():
            self.view_index = 0

    def add_update_new(self, gui_values: dict, sub_values: dict, window):
        """Add current configuration to state"""
        if self.validator.check_all_worker(self.dw, {**gui_values, **sub_values}):
            wkeys = self.key_manager.get_all_worker_keys(self.dw)
            method_key = self.key_manager.get_method_key(self.dw)
            ikeys = self.key_manager.get_all_interface_keys(self.dw, gui_values[method_key])
            wstate = {k: v for k, v in gui_values.items() if k in wkeys and not (':Optional:' in k and not v)}
            istate = {k: v for k, v in sub_values.items() if k in ikeys and not (':Optional:' in k and not v)}
            key_state = {**wstate, **istate}
            self.current = key_state
            view = self.converter.key_to_view(key_state)
            # Check if name already exists for this dataworker (update) else (append)
            if sum(match_states := [val.startswith(view.split('\n')[0]) for val in self.state]) > 0:
                if sum(match_states) > 1:
                    # Does not allow multiple same named dataworkers
                    raise NotImplementedError
                self.updated_state = True
                idx = match_states.index(True)
                self.state.insert(idx, view)
                self.state.pop(idx + 1)
            else:
                self.state.append(view)
            self.reset(window)
            if not self.view_index:
                self.view_index = 1
            exit_value = True
        else:
            sg.Popup("Something didn't check")
            exit_value = False
        return exit_value


class StateConverter:
    """Allows for converting between text configuration (var = value,) and GUI key dict {key: value,}"""
    def __init__(self, data_worker: str, key_manager: KeyManager):
        self.dw = data_worker
        self.meta_dw, __ = meta_data_objects()
        self.key_manager = key_manager

    def view_to_key(self, view_state: str):
        """Convert text configuration to GUI key dict"""
        list_of_lines = view_state.split('\n')
        view = dict(ConfigObj(list_of_lines))
        name, = list(view.keys())
        key_state = {self.key_manager.get_param_key_worker(self.dw, 'name'): name}
        parameters = view[name].pop('parameters', {})
        for k, v in view[name].items():
            key_state[self.key_manager.get_param_key_worker(self.dw, k)] = v
        for k, v in parameters.items():
            key_state[self.key_manager.get_param_key_interface(self.dw, view[name]['method'], k)] = v
        return key_state

    def key_to_view(self, key_state: dict):
        """Convert GUI key dict to text configuration"""
        state = deepcopy(key_state)
        name, = [k for k in state if k.endswith(':name')]
        name = state.pop(name)
        view = {name: {k.split(':')[-1]: v for k, v in state.items() if ':Worker:' in k}}
        view[name].update(self.key_to_parameters(state))
        return '\n'.join(ConfigObj(view).write())

    def key_to_parameters(self, key_state: dict):
        """Convert GUI key dict to parameter name dict"""
        params = {'parameters': {k.split(':')[-1]: v for k, v in key_state.items() if ':Interface:' in k}}
        if params.get('parameters') == {}:
            return {}
        else:
            return params


# Global state manager
default_state = MainDataWorkerStateManager()


class Updater:
    """Manages updating of options dependent on program state"""
    def __init__(self, main_data: MainData):
        self.key_manager = default_key_manager
        self.main_data = main_data
        self.state = default_state

    def u_columns(self, window, values):
        """Update possible columns for selecting"""
        for key in self.key_manager.get_update_keys('|column|'):
            if key in values.keys():
                window[key].update(values=self.main_data.get_columns())

    def u_neighborhood(self, window, values):
        """Update possible neighborhoods for selecting"""
        for key in self.key_manager.get_update_keys('|neighborhood|'):
            if key in values.keys():
                window[key].update(values=getattr(self.state, 'Neighborhoods').get_names())

    def u_filters(self, window, values):
        """Update possible filters for selecting"""
        for key in self.key_manager.get_update_keys('|filters|'):
            if key in values.keys():
                window[key].update(values=getattr(self.state, 'Filters').get_names())

    def u_recommender(self, window, values):
        """Update possible recommenders for selecting"""
        for key in self.key_manager.get_update_keys('|recommender|'):
            if key in values.keys():
                window[key].update(values=getattr(self.state, 'Recommenders').get_names())

    def u_metric(self, window, values):
        """Update possible metrics for selecting"""
        for key in self.key_manager.get_update_keys('|metric|'):
            if key in values.keys():
                window[key].update(values=getattr(self.state, 'Metrics').get_names())

    def u_metric_recommender(self, window, values, metric):
        """Update possible recommenders of a metric for selecting"""
        for key in self.key_manager.get_update_keys('|metric_recommender|'):
            if key in values.keys():
                window[key].update(values=getattr(self.state, 'Metrics').get_parameter(metric, 'rec_column', is_list=True), disabled=False)


class Dumper:
    """Writes the program state to file"""
    def __init__(self, data: MainData, file: str):
        self.meta_dw, __ = meta_data_objects()
        self.state = default_state
        self.data = data
        self.file = file
        self.text = ''
        self.update()

    def update(self):
        """Convert current program state to text"""
        output = {'DATA': self.data.dump()}
        for worker in self.meta_dw.get_dataworkers():
            output[(wkey := 'DW_' + worker)] = {}
            for state in getattr(self.state, worker).dump():
                if output[wkey] == {}:
                    output[wkey]['precedence'] = self.meta_dw.get_precedence(worker)
                output[wkey].update(dict(ConfigObj(state.split('\n'))))
            for specific_worker in output[wkey].keys():
                if specific_worker == 'precedence':
                    pass
                else:
                    if 'parameters' not in output[wkey][specific_worker].keys():
                        output[wkey][specific_worker]['parameters'] = {}
            if output[wkey] == {}:
                output.pop(wkey)
        # ConfigObj writer does not work as intended add an extra [ and ]
        self.text = '\n'.join([line.replace('[', '[[', 1).replace(']', ']]', 1) if ' [' in line else line
                               for line in ConfigObj(output).write()
                               ])

    def write(self):
        """Write current text program state to file"""
        with open(self.file, 'w') as writer:
            writer.write(self.text)
