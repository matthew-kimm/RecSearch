"""ConfigGenerator script runs through GUIs for generating experiment configuration files"""
import RecSearch.GetProgramLocation
from RecSearch.Config.ConfigGenMeta import MetaDataInterfaces, MetaDataWorkers
import PySimpleGUI as sg
from RecSearch.Config.ConfigGenLayout import MainDataWorkerLayoutManager
from RecSearch.Config.ConfigGenValidate import InputValidator
from RecSearch.Config.ConfigGenHelper import ConfigHelper
from RecSearch.Config.ConfigGenState import default_state, MainData, Updater, Dumper
from configobj import ConfigObj
from os.path import relpath, abspath

def config_generator():
    checker = InputValidator()
    helper = ConfigHelper()

    meta_dw = MetaDataWorkers()
    meta_di = MetaDataInterfaces()

    sg.theme('SystemDefault')

    start_layout = [[sg.Button('LOAD CONFIG')],
                    [sg.Button('NEW CONFIG')]]

    data_layout = [[sg.Text('datafile: '), sg.Input('', disabled=True, key='-datafile-', enable_events=True),
                    sg.FileBrowse(file_types=(('CSV', '*.csv'),))],
                   [sg.Checkbox('Relative Path', default=False, key='-rel_path-', enable_events=True)],
                   [sg.Text('Use Columns: '), sg.Listbox([], key='-use_columns-', select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,
                    size=(30, 10), enable_events=True)],
                   [sg.Text('Index: '), sg.Listbox([], key='-index_columns-', select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,
                    size=(30, 10))],
                   [sg.Text('List/Dict Columns: '), sg.Listbox([], key='-ast_columns-', select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,
                    size=(30, 10))],
                   [sg.Button('Save Data Config')]]


    # Main Layout and Sub Layouts

    manager = MainDataWorkerLayoutManager()

    data_worker_layout = [[sg.TabGroup([[sg.Tab('Splitters', manager.get_layout('Splitters')),
                                         sg.Tab('Filters', manager.get_layout('Filters')),
                                         sg.Tab('Neighborhoods', manager.get_layout('Neighborhoods')),
                                         sg.Tab('Recommenders', manager.get_layout('Recommenders')),
                                         sg.Tab('Metrics', manager.get_layout('Metrics')),
                                         sg.Tab('Comparers', manager.get_layout('Comparers'))]])]]

    save_layout = [[sg.Text('Output Config File: '), sg.Input('', disabled=True, key='-output_config_file-', enable_events=True),
                    sg.SaveAs(file_types=(('CFG', '*.cfg'),))],
                   [sg.Button('Save to File', key=':Dump:')]]

    layout = [[sg.TabGroup([[sg.Tab('DataWorkers', data_worker_layout),
                             sg.Tab('Save', save_layout, key='-save-')]])]]


    # START WINDOW
    start_window = sg.Window('RecSearch Config Generator Start', start_layout)
    closed = False
    load_config = ''
    while True:
        start_event, start_values = start_window.read()
        if start_event == sg.WIN_CLOSED:
            closed = True
            break
        elif start_event == 'NEW CONFIG':
            break
        elif start_event == 'LOAD CONFIG':
            load_config = sg.PopupGetFile('Load Config File', file_types=(('CFG', '*.cfg'),))
            break

    start_window.close()


    # DATA WINDOW
    data_window = sg.Window('RecSearch Config Generator Data', data_layout)
    main_data = None
    updater = None
    data_init = False
    while True:
        if closed:
            break
        if not data_init:
            data_event, data_values = data_window.read(timeout=100)
            if load_config:
                main_data = MainData(dataconfig=ConfigObj(load_config)['DATA'])
                data_window['-datafile-'].update(main_data.get_datafile())
                data_window['-use_columns-'].update(main_data.get_columns())
                data_window['-use_columns-'].set_value(main_data.get_use_columns())
                data_window['-index_columns-'].update(main_data.get_columns())
                data_window['-index_columns-'].set_value(main_data.get_index())
                data_window['-ast_columns-'].update(main_data.get_columns())
                data_window['-ast_columns-'].set_value(main_data.get_ast_columns())
            data_init = True

        data_event, data_values = data_window.read()
        if data_event == sg.WIN_CLOSED:
            closed = True
            break

        if data_event == '-datafile-':
            try:
                data_window['-rel_path-'].update(False)
                main_data = MainData(data_values['-datafile-'])
                data_window['-use_columns-'].update(main_data.get_columns())
            except NotImplementedError:
                pass

        if data_event == '-rel_path-':
            if data_values['-datafile-']:
                if data_values['-rel_path-']:
                    data_window['-datafile-'].update(relpath(data_values['-datafile-']))
                else:
                    data_window['-datafile-'].update(abspath(data_values['-datafile-']))
            else:
                data_window['-rel_path-'].update(False)

        if data_event == '-use_columns-':
            data_window['-index_columns-'].update(data_values['-use_columns-'])
            data_window['-ast_columns-'].update(data_values['-use_columns-'])

        if data_event == 'Save Data Config':
            main_data.finish(data_values['-use_columns-'], data_values['-index_columns-'], data_values['-ast_columns-'],
                             data_values['-datafile-'])
            break

    data_window.close()
    updater = Updater(main_data)

    # Main Layout Window
    window = sg.Window('RecSearch Config Generator Experiment', layout)

    def update_view(udw: str):
        window[':current:' + udw].update(getattr(default_state, udw).message())
        window[':preview:' + udw].update(getattr(default_state, udw).get_view_state())

    initialize = False
    sub_values = {}
    while True:
        if closed:
            break
        if not initialize:
            event, values = window.read(timeout=100)
            if load_config:
                default_state.load(load_config)
                [update_view(udw) for udw in meta_dw.get_dataworkers()]

            for name in meta_dw.get_dataworkers():
                # Initialize methods and data columns for choosing
                for value in values.keys():
                    if str(value).endswith(':method'):
                        window[value].update(values=meta_di.get_interfaces(value.split(':')[-2]))
                    if str(value).startswith('|column|'):
                        window[value].update(values=main_data.get_columns())
                # Populate Key Manager for Sub-Windows
                for interface in meta_di.get_interfaces(name):
                    manager.set_interface(name, interface)
                    manager.set_popup(name)
                manager.set_interface(name, '')
                manager.set_popup(name)

            initialize = True
        else:
            event, values = window.read()
        #print(event)
        #print(values)
        if event == sg.WIN_CLOSED:
            break

        if event.endswith(':method'):
            manager.set_interface(event.split(':')[-2], values[event])
            getattr(default_state, event.split(':')[-2]).change_method(values[event])

        if event.startswith(':Interface:Launch:'):
            dw = event.split(':')[-1]
            manager.set_popup(dw)
            sub_layout = manager.get_popup(dw)
            sub_window = sg.Window(event, sub_layout, resizable=True, size=(800, 600))
            sub_init = False
            while True:
                if not sub_init:
                    sub_event, sub_values = sub_window.read(timeout=100)
                    updater.u_columns(sub_window, sub_values)
                    updater.u_neighborhood(sub_window, sub_values)
                    updater.u_filters(sub_window, sub_values)
                    updater.u_recommender(sub_window, sub_values)
                    updater.u_metric(sub_window, sub_values)
                    if getattr(default_state, dw).get_persist():
                        def get_locs(super_list: list, sub_list: list):
                            """
                            Gets integer locations of previously selected values needed for reselection in a combobox/listbox
                            :param super_list: list containing the values to reselect
                            :param sub_list: values to reselect
                            :return:
                            """
                            locs = []
                            for sub_key in sub_list:
                                locs.append(super_list.index(sub_key))
                            return locs

                        for key, value in getattr(default_state, dw).get_current().items():
                            if type(sub_window[key]) == sg.Input:
                                sub_window[key].update(value=value)
                            elif type(sub_window[key]) == sg.Combo:
                                try:
                                    sub_window[key].update(set_to_index=get_locs(getattr(sub_window[key], 'Values'), [value,]))
                                except ValueError:
                                    pass
                            elif type(sub_window[key]) == sg.Listbox:
                                sub_window[key].update(set_to_index=get_locs(sub_window[key].get_list_values(), value))
                    sub_event, sub_values = sub_window.read(timeout=100)
                    sub_init = True
                sub_event, sub_values1 = sub_window.read()
                sub_values = sub_values1 if sub_values1 is not None else sub_values
                #print(sub_event)
                #print(sub_values)
                if sub_event == sg.WIN_CLOSED:
                    if getattr(default_state, dw).get_persist():
                        getattr(default_state, dw).persist(sub_values)
                    break
                if sub_event.startswith(':Submit:Popup:'):
                    getattr(default_state, dw).persist(sub_values)
                    break
                if sub_event.endswith(':Check'):
                    sg.Popup(checker.individual_check(sub_event, sub_values))
                if sub_event.endswith(':Help'):
                    sg.Popup(helper.get_help_string(sub_event))
                if sub_event.startswith('|metric|'):
                    updater.u_metric_recommender(sub_window, sub_values, sub_values[sub_event])
                if sub_event.startswith('&Rel&'):
                    file_param_key = sub_event.removeprefix('&Rel&')
                    if sub_values[sub_event]:
                        try:
                            sub_window[file_param_key].update(relpath(sub_values[file_param_key]))
                        except ValueError:
                            sub_window[sub_event].update(False)
                    else:
                        sub_window[file_param_key].update(abspath(sub_values[file_param_key]))
            sub_window.close()

        if event.endswith(':Check'):
            sg.Popup(checker.individual_check(event, values))

        if event.endswith(':Help'):
            sg.Popup(helper.get_help_string(event))

        if event.startswith(':update:'):
            dw = event.split(':')[2]
            try:
                all_values_for_update = getattr(default_state, dw).add_update_new(values, sub_values, window)
            except KeyError:
                all_values_for_update = False
                sg.Popup('Need to Configure Interface')
            if all_values_for_update:
                message = getattr(default_state, dw).message()
                window[':current:' + dw].update(message)
                if getattr(default_state, dw).end() == getattr(default_state, dw).idx():
                    window[':preview:' + dw].update(getattr(default_state, dw).get_view_state())
                elif getattr(default_state, dw).get_updated_state():
                    window[':preview:' + dw].update(getattr(default_state, dw).get_view_state())

        if event.startswith(':>:'):
            dw = event.split(':')[2]
            getattr(default_state, dw).increment()
            update_view(dw)

        if event.startswith(':<:'):
            dw = event.split(':')[2]
            getattr(default_state, dw).decrement()
            update_view(dw)

        if event.startswith(':>>:'):
            dw = event.split(':')[2]
            getattr(default_state, dw).ending()
            update_view(dw)

        if event.startswith(':<<:'):
            dw = event.split(':')[2]
            getattr(default_state, dw).beginning()
            update_view(dw)

        if event.startswith(':default:'):
            # Doesn't Work yet
            dw = event.split(':')[2]
            getattr(default_state, dw).reset(window)

        if event.startswith(':remove:'):
            dw = event.split(':')[2]
            getattr(default_state, dw).remove()
            update_view(dw)

        if event.startswith(':edit:'):
            dw = event.split(':')[2]
            getattr(default_state, dw).edit(window, values)
            manager.set_interface(dw, getattr(default_state, dw).get_di())

        if event == ':Dump:':
            if filename := values['-output_config_file-']:
                saver = Dumper(main_data, filename)
                saver.write()

    window.close()
    default_state.reset_state()


if __name__ == '__main__':
    config_generator()
