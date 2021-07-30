import RecSearch.GetProgramLocation
import PySimpleGUI as sg
from os.path import sep as os_sep
from os.path import relpath, abspath, exists
from os import mkdir
import configparser
import ast
import numpy as np
import glob
import pandas as pd
from RecSearch.Main.Experiment import Experiment
pd.options.mode.chained_assignment = None


def write_experiment_configs(folder_location, base_cfg_file, variations, n_variations, repeats):
    """Write .cfgs for experiments with varying parameter or repeats"""
    with open(base_cfg_file, 'r') as default_cfg_file:
        base_cfg_lines = default_cfg_file.readlines()

    def order_str(number, possible):
        """For ordering experiment files numerically e.g. experiment 1 of 100 -> 001"""
        final_digits = len(str(possible))
        current_digits = len(str(number))
        prefix_zeros = final_digits - current_digits
        return '0' * prefix_zeros + str(number)

    def replace_cfg(original, key, value):
        """Replace base parameter value with varied value"""
        start = 0
        for location in key.split('.'):
            found_in_original = [location in line for line in original]
            try:
                new_start = found_in_original.index(True, start)
            except ValueError:
                sg.Popup('Parameter can not be found in base configuration.')
                return False
            start = new_start
        original_line = original[start]
        original_param_pair = original_line.split(' = ')
        if len(original_param_pair) != 2:
            sg.Popup('Error: splitting on = does not result in key, value pair.')
            return False
        else:
            original_param_key = original_param_pair[0]
        new_line = ' = '.join([original_param_key, str(value)])
        new_cfg = original
        new_cfg[start] = new_line
        return new_cfg

    if n_variations != 0:
        varied_configs_to_repeat = []
    else:
        varied_configs_to_repeat = ['\n'.join(base_cfg_lines),]
    for i in range(0, n_variations):
        new_base_cfg_lines = base_cfg_lines
        for k, v in variations.items():
            new_base_cfg_lines = replace_cfg(new_base_cfg_lines, k, v[i])
        varied_configs_to_repeat.append('\n'.join(new_base_cfg_lines))

    n_varied_experiments = len(varied_configs_to_repeat)
    if not exists(folder_location):
        if not exists(exp_folder := os_sep.join(folder_location.split(os_sep)[:-2])):
            mkdir(exp_folder)
        mkdir(folder_location)
    for i in range(0, n_varied_experiments):
        for j in range(0, repeats):
            with open(folder_location + 'experiment_' + order_str(i, n_variations) + '_'\
                      + order_str(j, repeats) + '.cfg', 'w') as write_file:
                write_file.write(varied_configs_to_repeat[i])

    return True


def run_experiment_configs(folder_location, load_experiment, starting_seed):
    """Run the experiments with progress bar"""
    experiments = sorted(glob.glob(folder_location + os_sep + '*.cfg'))
    number_of_experiments = len(experiments)
    for i, experiment in enumerate(experiments):
        continue_exp = sg.one_line_progress_meter('Experiments Progress', i, number_of_experiments, '-progress-',
                                   'RecSearch Progress\nPressing Cancel will cancel the run on the next iteration.')
        if not continue_exp:
            break
        experiment_name = experiment.split(os_sep)[-1]
        variation_num, repeat_num = [int(num) for num in experiment_name.removesuffix('.cfg').split('_')[1:]]
        experiment_path = experiment.removesuffix('.cfg') + os_sep
        np.random.seed(starting_seed + repeat_num)
        if exists(experiment_path):
            if load_experiment:
                my_experiment = Experiment(experiment, load=True)
            else:
                my_experiment = Experiment(experiment)
        else:
            my_experiment = Experiment(experiment)
        my_experiment.run()
        continue_exp = sg.one_line_progress_meter('Experiments Progress', i+1, number_of_experiments, '-progress-', 'RecSearch Progress')
        if not continue_exp:
            break
    sg.popup_ok('Finished')


def run_experiment_ini():
    """Main GUI for running experiments"""
    sg.theme('SystemDefault')

    layout = [[sg.Text('Experiment(s) INI file:')],
              [sg.Input(disabled=True, key='-ini-', enable_events=True), sg.FileBrowse(file_types=(('INI', '*.ini'),))],
              [sg.Checkbox('Relative Path', key='-relpath-', enable_events=True)],
              [sg.Checkbox('Load/Continue Experiment', default=True, key='-load-')],
              [sg.Checkbox('Extend (Changed INI to Extend)', default=False, key='-extend-')],
              [sg.Text('Output Folder (Experiment Data):')],
              [sg.Input(disabled=True, key='-output-')],
              [sg.Button('Run', disabled=True)]]

    window = sg.Window('Run Experiment', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == '-ini-':
            ini_value = values['-ini-'].replace('/', os_sep)
            ini_folder = os_sep.join(ini_value.split(os_sep)[:-1]) + os_sep
            ini_file_name = ini_value.split(os_sep)[-1].removesuffix('.ini')
            ini_output_path = ini_folder + ini_file_name + os_sep + 'Results' + os_sep
            window['-output-'].update(ini_output_path)
            window['-relpath-'].update(False)
            window['Run'].update(disabled=False)
        if event == '-relpath-':
            if file := values['-ini-']:
                if values['-relpath-']:
                    window['-ini-'].update(relpath(file))
                    window['-output-'].update(relpath(values['-output-']))
                else:
                    window['-ini-'].update(abspath(file))
                    window['-output-'].update(abspath(values['-output-']))
            else:
                window['-relpath-'].update(False)

        if event == 'Run':
            ini_file = values['-ini-']
            load = values['-load-']
            extend = values['-extend-']
            result_folder = values['-output-']
            ini_parser = configparser.RawConfigParser()
            ini_parser.optionxform = lambda option: option
            ini_parser.read(ini_file)
            ini = dict({k: dict(v) for k, v in ini_parser.items()})
            base = ini['EXP']['experiment']
            seed = int(ini['EXP']['seed'])
            repeat = int(ini['EXP']['repeat'])
            vary_exist = ini.get('VARY', {})
            vary = {k: ast.literal_eval(v) for k, v in vary_exist.items()}

            def expand(collection):
                if type(collection) == set:
                    output = list(collection)
                elif type(collection) == list:
                    start = collection[0]
                    stop = collection[1]
                    if len(collection) == 2:
                        output = list(np.arange(start, stop))
                    elif len(collection) == 3:
                        step = collection[2]
                        output = list(np.arange(start, stop, step))
                    elif len(collection) == 4:
                        step = collection[2]
                        round_digits = collection[3]
                        output = [round(v, round_digits) for v in np.arange(start, stop, step)]
                return output

            valid_vary = True
            n = 0
            if vary:
                vary = {k: expand(v) for k, v in vary.items()}
                n = len(list(vary.values())[0])
                if not all([len(v) == n for v in vary.values()]):
                    sg.Popup('Error: variations differ in size.')
                    valid_vary = False

            if valid_vary:
                write_success = True  # or no writing implying writing has already been successful.
                if extend or not load:
                    write_success = write_experiment_configs(ini_output_path, base, vary, n, repeat)
                if write_success:
                    run_experiment_configs(result_folder, load, seed)

    window.close()


if __name__ == '__main__':
    run_experiment_ini()
