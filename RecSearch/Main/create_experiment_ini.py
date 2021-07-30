from RecSearch import GetProgramLocation
import PySimpleGUI as sg
from RecSearch.ExperimentSupport.ExperimentParameters import ExperimentParameters
from os.path import relpath, abspath
from os import sep as os_sep
import ast
import configparser


closed = False


def get_config_file():
    """GUI for loading .cfg file for forming .ini file"""
    global closed
    sg.theme('SystemDefault')

    layout = [[sg.Text('Experiment Config')],
              [sg.Input(disabled=True, key='-config-', enable_events=True), sg.FileBrowse(file_types=(('CFG', '*.cfg'),))],
              [sg.Checkbox('Relative Path', enable_events=True, key='-relpath-')],
              [sg.Button('Get')]
             ]

    window = sg.Window('Base CFG for Experiment INI', layout)

    while True:
        if closed:
            break
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            closed = True
            break
        if event == 'Get':
            break
        if event == '-relpath-':
            if file := values['-config-'].replace('/', os_sep):
                if values['-relpath-']:
                    window['-config-'].update(relpath(file))
                else:
                    window['-config-'].update(abspath(file))
            else:
                window['-relpath-'].update(False)
        if event == '-config-':
            window['-relpath-'].update(False)

    window.close()
    if not closed:
        output = values['-config-']
    else:
        output = ''
    return output


def create_experiment_ini():
    """GUI for creating ini file"""
    global closed
    closed = False
    ini = configparser.RawConfigParser()
    ini.optionxform = lambda option: option

    sg.theme('SystemDefault')

    base_cfg = get_config_file()
    vary_values = get_vary_parameter(base_cfg)
    seed, repeat = get_additional_experiments_config()

    ini['EXP'] = {'experiment': base_cfg, 'seed': seed, 'repeat': repeat}
    if vary_values:
        ini['VARY'] = vary_values

    layout = [[sg.Text('Output File:')],
              [sg.Input(disabled=True, key='-ini-'), sg.SaveAs(file_types=(('INI', '*.ini'),))],
              [sg.Button('Save')]]

    window = sg.Window('Save INI', layout)
    while True:
        if closed:
            break
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            closed = True
            break
        elif event == 'Save':
            if file := values['-ini-']:
                with open(file, 'w') as configfile:
                    ini.write(configfile)

    window.close()


def get_vary_parameter(base_cfg):
    """GUI for selecting parameter to vary and how."""
    global closed
    tree_dict = ExperimentParameters(base_cfg).cfg()

    def folder(base, location):
        fkey = '' if not base else base + '.'
        return fkey + location

    def file(base, location):
        return base + '.' + location

    def walk(node, treedata, last_folder):
        for key, value in node.items():
            if isinstance(value, dict):
                node_key = folder(last_folder, key)
                treedata.Insert(last_folder, node_key, key, [])
                local_last_folder = node_key
                walk(value, treedata, local_last_folder)
            else:
                node_key = file(last_folder, key)
                treedata.Insert(last_folder, node_key, key, value)

    tree_data = sg.TreeData()
    walk(tree_dict, tree_data, '')

    layout = [[sg.Text('Experiment Config:')],
              [sg.Text(base_cfg)],
              [sg.Text()],
              [sg.Text('Select Instances of Parameter to Vary:')],
              [sg.Tree(data=tree_data, headings=['Value'], key='-tree-', select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                       show_expanded=True, max_col_width=50, col0_width=50, def_col_width=50, auto_size_columns=False)],
              [sg.Text("Vary Values: (either specify: {'abc',5,}"
                       "or range: [start, stop, step (default=1), round (default=2)])")],
              [sg.Input(key='-vary-')],
              [sg.Text()],
              [sg.Button('Submit/Continue')]
             ]

    window = sg.Window('Create_Exeriment_INI', layout)
    output = {}
    while True:
        if closed:
            break
        if base_cfg is None or base_cfg == '':
            break
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            closed = True
            break
        if event == 'Submit/Continue':
            correct = ''
            if values['-tree-'] and not values['-vary-']:
                sg.Popup('Parameter selected but not varied.')
            elif not values['-tree-'] and values['-vary-']:
                sg.Popup('No Parameter selected for the given variation.')
            elif not values['-tree-'] and not values['-vary-']:
                correct = 'Yes'
            else:
                check = ''
                try:
                    check = ast.literal_eval(values['-vary-'])
                except (ValueError, SyntaxError):
                    sg.Popup('Vary values could not be parsed.')
                if check:
                    if type(check) == set:
                        pass
                    elif type(check) == list:
                        is_numeric = all(isinstance(v, (int, float)) for v in check)
                        if not is_numeric:
                            sg.Popup('List has non-numeric value.')
                        is_required_length = len(check) in [2, 3, 4]
                        if not is_required_length:
                            sg.Popup('List length should be 2-4.')
                    else:
                        check = ''
                        sg.Popup('Invalid type for variation, must be list or set.')
                    if check:
                        correct = sg.popup_scrolled('Is this correct (Editing this text block has no effect):'\
                                                    + '\n\nKeys:\n'\
                                                    + '\n'.join(values['-tree-'])\
                                                    + '\n\nVary:\n' + values['-vary-'], yes_no=True)
            if correct == 'Yes':
                for key in values['-tree-']:
                    output[key] = values['-vary-']
                break

    window.close()

    return output


def get_additional_experiments_config():
    """GUI for getting additional experiment configuration"""
    global closed
    layout = [[sg.Text('Starting Random Seed (Integer)')],
              [sg.Input('1', key='-seed-')],
              [sg.Text('Repeat Experiment (Integer):')],
              [sg.Input('1', key='-repeat-')],
              [sg.Button('Add to Configuration')]]

    window = sg.Window('Additional Experiment(s) INI Config', layout)
    seed, repeat = (1, 1)
    while True:
        if closed:
            break
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Add to Configuration':
            seed, repeat = (values['-seed-'], values['-repeat-'])
            break

    window.close()
    return seed, repeat


if __name__ == '__main__':
    create_experiment_ini()
