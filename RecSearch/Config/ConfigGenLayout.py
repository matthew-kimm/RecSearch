from RecSearch.Config.ConfigGenMeta import meta_data_objects
import PySimpleGUI as sg
from RecSearch.Config.ConfigGenInputDef import InputFunctions
from RecSearch.Config.ConfigGenKeyManage import KeyManager, default_key_manager


class MainDataWorkerLayoutManager:
    """Manages DataWorker/Interface GUI Layout Creation for all DataWorkers."""
    def __init__(self):
        self.meta_dw, __ = meta_data_objects()
        self.key_manager = default_key_manager
        for worker in self.meta_dw.get_dataworkers():
            setattr(self, worker, MainDataWorkerLayout(worker, getattr(self.key_manager, worker)))

    def get_layout(self, worker: str) -> list[list]:
        """Get a DataWorker main layout (DataWorker parameters but not it's interfaces parameters)"""
        return getattr(self, worker).get_layout()

    def get_popup(self, worker: str) -> list[list]:
        """Get a DataWorker Interface layout for interface parameters"""
        return getattr(self, worker).get_popup()

    def set_interface(self, worker: str, interface: str) -> None:
        """Set the DataWorker Interface"""
        getattr(self, worker).set_interface(interface)

    def set_popup(self, worker: str) -> None:
        """Set the DataWorker Interface layout for the currently set interface"""
        getattr(self, worker).set_popup()


class MainDataWorkerLayout:
    """Manages DataWorker/Interface GUI Layout Creation for its DataWorker."""
    def __init__(self, data_worker: str, key_manager: KeyManager):
        self.meta_dw, self.meta_di = meta_data_objects()
        self.input_generator = InputFunctions()
        self.dw = data_worker
        self.di = ''
        self.key_manager = key_manager
        self.view_layout = [[sg.Button('Add/Update', key=(ukey := ':update:' + self.dw)),
                             sg.Button('Edit', key=(ekey := ':edit:' + self.dw)),
                             sg.Button('Remove', key=(xkey := ':remove:' + self.dw)),
                             sg.Button('Default', key=(dkey := ':default:' + self.dw))],
                            [sg.Text('Preview'), sg.Multiline(size=(75, 25), key=(pkey := ':preview:' + self.dw))],
                            [sg.Button('<<', key=(llkey := ':<<:' + self.dw)),
                             sg.Button('<', key=(lkey := ':<:' + self.dw)),
                             sg.Text('0   /   0', key=(ckey := ':current:' + self.dw)),
                             sg.Button('>', key=(rkey := ':>:' + self.dw)),
                             sg.Button('>>', key=(rrkey := ':>>:' + self.dw))]]
        self.key_manager.update_main_keys([ukey, ekey, xkey, dkey, pkey, llkey, lkey, ckey, rkey, rrkey])

        # Set Data Worker Parameters Layout
        self.set_options()

        # Set Interface Parameters Layout
        self.set_popup()

        # Construct Data Worker Parameter Layout
        self.dw_layout = [[sg.TabGroup([[sg.Tab('Required', self.dw_required_layout,
                                                key=':Worker:Required:' + self.dw),
                                         sg.Tab('Optional', self.dw_optional_layout,
                                                key=':Worker:Optional:' + self.dw)]])]]

        # Interface Launcher Layout
        self.di_launch_layout = [[sg.Button('Launch', key=(ikey := ':Interface:Launch:' + self.dw))]]
        self.key_manager.update_main_keys([ikey])

        # Set Overall DataWorker Layout
        self.layout = [[sg.TabGroup([[sg.Tab('View', self.view_layout, key=':View:' + self.dw),
                                      sg.Tab('Worker Config', self.dw_layout, key=':Worker:' + self.dw),
                                      sg.Tab('Interface Config', self.di_launch_layout, key=':Interface:' + self.dw,
                                             element_justification='c')]])
                        ]]

    def get_layout(self) -> list[list]:
        """Get DataWorker main layout (DataWorker parameters but not it's interfaces parameters)"""
        return self.layout

    def class_config_to_layout(self, param_dict: dict, param_type: str, interface_name: str = '') -> list[list]:
        """Use the class attribute cfg sub-dictionary (required/optional) to create layout."""
        layout = []
        base_key = ''
        if param_type == 'Required':
            if not interface_name:
                base_key = self.key_manager.get_dw_req_base()
            else:
                base_key = self.key_manager.get_di_req_base(interface_name)
        elif param_type == 'Optional':
            if not interface_name:
                base_key = self.key_manager.get_dw_opt_base()
            else:
                base_key = self.key_manager.get_di_opt_base(interface_name)
        # Generate layout
        for param, param_config in param_dict.items():
            layout.append(self.input_generator.call_input(param_config['input'], param, param_config['validate'],
                                                          base_key=base_key, key_manager=self.key_manager))
        return layout

    def set_interface(self, interface) -> None:
        """Set the DataWorker Interface"""
        self.di = interface

    def set_options(self) -> None:
        """Set the DataWorker (not its interface) parameter layout for required/optional."""
        self.dw_required_layout = self.class_config_to_layout(self.meta_dw.get_required(self.dw), 'Required')
        self.dw_optional_layout = self.class_config_to_layout(self.meta_dw.get_optional(self.dw), 'Optional')

    def set_popup(self) -> None:
        """Set the DataWorker Interface parameter layout"""
        if self.di:
            self.di_required_layout = self.class_config_to_layout(self.meta_di.get_required(self.dw, self.di), 'Required', self.di)
            self.di_optional_layout = self.class_config_to_layout(self.meta_di.get_optional(self.dw, self.di), 'Optional', self.di)
        else:
            self.di_required_layout = [[]]
            self.di_optional_layout = [[]]

        self.di_required_layout += [[sg.Button('Submit', key=':Submit:Popup:' + self.dw)]]

        self.di_edit_layout = [[sg.Column([[sg.TabGroup(
                                [[sg.Tab('Required', self.di_required_layout, key=':Required:Interface:' + self.dw),
                                  sg.Tab('Optional', self.di_optional_layout, key=':Optional:Interface:' + self.dw),
                                 ]])
                                ]], scrollable=True, expand_x=True, expand_y=True)]]

    def get_popup(self) -> list[list]:
        """Get the DataWorker Interface parameter layout"""
        return self.di_edit_layout
