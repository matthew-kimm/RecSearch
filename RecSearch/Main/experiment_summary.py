from RecSearch import GetProgramLocation
import PySimpleGUI as sg
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import configparser
from os.path import sep as os_sep
import glob
from string import ascii_lowercase
from os.path import relpath, abspath, exists
from os import mkdir
import re
import ast
from RecSearch.Stats.corrected_resampled_t_test import corrected_resampled_t_statistic
from typing import Union
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


sg.theme('SystemDefault')


def call_sub_gui(func, parent_window):
    parent_window.hide()
    func()
    parent_window.un_hide()


def generate_experiment_sum():
    """Generate Experiment Summary Configuration GUI"""
    tree_data = sg.TreeData()

    layout = [[sg.Text('Experiment INI:')],
              [sg.Input(disabled=True, key='-INI-', enable_events=True), sg.FileBrowse(file_types=(('INI', '*.ini'),))],
              [sg.Checkbox('Relative Path', enable_events=True, key='-relpath-')],
              [sg.Text('Summary Name:')],
              [sg.Input('my_summary', key='-name-')],
              [sg.Text('Comparer Variable Mappings:')],
              [sg.Tree(data=tree_data, headings=['Variable'], key='-tree-', select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                       show_expanded=True, max_col_width=50, col0_width=50, def_col_width=50, auto_size_columns=False)],
              [sg.Text('Expression: Aggregation Function (++ sum, // mean), Variable, [optional] 4 function (+,-,/,*), ...')],
              [sg.Text('e.g. ++a; e.g. ++a/++b')],
              [sg.Input(key='-expression-')],
              [sg.Text('Summary SUM file output:')],
              [sg.Input(disabled=True, key='-SUM-'), sg.SaveAs(file_types=(('SUM', '.sum'),))],
              [sg.Button('Save')]]

    window = sg.Window('Experiment Summary', layout)

    variable_mappings = {}
    experiment_ini = ''
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == '-relpath-':
            if ini_path := values['-INI-'].replace('/', os_sep):
                if values['-relpath-']:
                    window['-INI-'].update(new_path := relpath(ini_path))
                else:
                    window['-INI-'].update(new_path := abspath(ini_path))
                experiment_ini = new_path
            else:
                window['-relpath-'].update(False)
        if event == '-INI-':
            window['-relpath-'].update(False)
            variable_mappings = {}
            experiment_ini = values['-INI-']
            tree_data = sg.TreeData()
            exp_folder = values['-INI-'].removesuffix('.ini') + os_sep
            exp_folder += 'Results' + os_sep
            exp_sub_folders = glob.glob(exp_folder + '*' + os_sep)
            check_file = exp_sub_folders[0] + 'test.csv'
            experiment_columns = pd.read_csv(check_file, nrows=0)
            comparers = list(pd.Series(
                [col.split('R__')[0] for col in experiment_columns if col.startswith('C__')]).unique())
            for i, comparer in enumerate(comparers):
                variable_letter = ascii_lowercase[i]
                tree_data.Insert('', variable_letter, comparer, variable_letter)
                variable_mappings[variable_letter] = comparer
            window['-tree-'].update(tree_data)
        if event == 'Save':
            if values['-INI-'] and values['-expression-'] and values['-SUM-'] and values['-name-']:
                sum_output = configparser.RawConfigParser()
                sum_output.optionxform = lambda option: option
                sum_output['EXP'] = {'name': values['-name-'], 'experiment': experiment_ini}
                variable_mappings.update({'expression': values['-expression-']})
                sum_output['SUM'] = variable_mappings
                with open(values['-SUM-'], 'w') as file:
                    sum_output.write(file)
    window.close()


def get_results(expression, data):
    exp = expression['expression']
    agg_funcs = {'++': 'sum', '//': 'mean'}
    summary_columns = re.findall('[+]{2}[a-z]{1}|[/]{2}[a-z]{1}', exp)
    comparer_columns = [col for col in data.columns if col.startswith('C__')]
    recommenders = list(pd.Series([col.split('R__')[1] for col in comparer_columns]).unique())
    for col in summary_columns:
        exp = exp.replace(col, col[2])
    if len(re.findall('[a-z]{2,}', exp)) > 0:
        print('Error: Summary Expression has words of length 2 or larger.')
        raise ValueError
    results = {}
    for recommender in recommenders:
        agg_values = {token[2]: data[expression[token[2]] + 'R__' + recommender].agg(
            agg_funcs[token[:2]]) for token in summary_columns}
        agg_frame = pd.DataFrame(agg_values, index=[0])
        result = agg_frame.eval(exp).loc[0]
        results[recommender] = result
    return results


def gather_results(expression: dict, result_folder: str, summary_folder: str):
    experiment_results_folders = glob.glob(result_folder + '*' + os_sep)
    df = pd.DataFrame(columns=['Vary', 'Repeat', 'Value'])
    max_value = len(experiment_results_folders)
    for i, experiment_folder in enumerate(experiment_results_folders):
        continue_sum = sg.one_line_progress_meter('Gathering Results', i, max_value)
        if not continue_sum:
            break
        experiment = experiment_folder.split(os_sep)[-2]
        vary = experiment.split('_')[1]
        repeat = experiment.split('_')[2]
        test_data_file = experiment_folder + os_sep + 'test.csv'
        test_data = pd.read_csv(test_data_file)
        results = get_results(expression, test_data)
        if results == {}:
            print('Error: Results empty for experiment_' + str(vary) + '_' + str(repeat))
            raise ValueError
        for recommender, value in results.items():
            df = df.append({'Vary': vary, 'Repeat': repeat, 'Recommender': recommender, 'Value': value}, ignore_index=True)
        continue_sum = sg.one_line_progress_meter('Gathering Results', i + 1, max_value)
        if not continue_sum:
            break
    df.to_csv(summary_folder + 'all.csv', index=False)
    sg.Popup('Finished')


def run_experiment_sum():
    layout = [[sg.Text('Summary File (SUM):')],
              [sg.Input(disabled=True, key='-SUM-'), sg.FileBrowse(file_types=(('SUM', '.sum'),))],
              [sg.Button('Run')]]

    window = sg.Window('Run Summary', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Run' and (sum_file := values['-SUM-']):
            with open(sum_file, 'r') as file:
                sum_parser = configparser.RawConfigParser()
                sum_parser.optionxform = lambda option: option
                sum_parser.read_file(file)
            name = sum_parser['EXP']['name']
            experiment_ini = sum_parser['EXP']['experiment']
            experiment_folder = experiment_ini.removesuffix('.ini') + os_sep
            experiment_result_folder = experiment_folder + 'Results' + os_sep
            experiment_summary_folder = experiment_folder + 'Summary' + os_sep + name + os_sep
            if not exists(experiment_summary_folder):
                if not exists(parent := os_sep.join(experiment_summary_folder.split(os_sep)[:-2])):
                    mkdir(parent)
                mkdir(experiment_summary_folder)
            expression = dict(sum_parser['SUM'])
            gather_results(expression, experiment_result_folder, experiment_summary_folder)
    window.close()


def convert_varies_base(v_base: Union[list, set]):
    if type(v_base) == list:
        if len(v_base) < 4:
            vary_values = np.arange(*v_base)
        else:
            vary_values = [round(num, v_base[3]) for num in np.arange(*v_base[:3])]
    elif type(v_base) == set:
        vary_values = list(v_base)
    else:
        print('Vary is not a list or set.')
        raise ValueError
    return vary_values


def summary_table():
    """Summary Tables GUI"""
    sum_file = sg.popup_get_file('Select .sum file for table.', 'Select .sum file', file_types=(('SUM', '.sum'),))
    with open(sum_file, 'r') as file:
        sum_parser = configparser.RawConfigParser()
        sum_parser.optionxform = lambda option: option
        sum_parser.read_file(file)

    ini_file = sum_parser['EXP']['experiment']
    with open(ini_file, 'r') as file:
        ini_parser = configparser.RawConfigParser()
        ini_parser.optionxform = lambda option: option
        ini_parser.read_file(file)

    repeats = ini_parser['EXP']['repeat']
    try:
        vary_config = ini_parser['VARY']
        varies_base = ast.literal_eval(vary_config[list(vary_config.keys())[0]])
        # Behavior is somewhat repeated in run_experiment_ini
        varies = convert_varies_base(varies_base)
    except KeyError:
        varies = [0,]
    n_varies = len(varies)
    results_folder = ini_file.removesuffix('.ini') + os_sep + 'Results' + os_sep
    results_folders = glob.glob(results_folder + '*' + os_sep)
    sample_folder = results_folders[0]
    sample_train_data = pd.read_csv(sample_folder + 'train.csv')
    sample_test_data = pd.read_csv(sample_folder + 'test.csv')
    n1 = sample_train_data.shape[0]
    n2 = sample_test_data.shape[0]
    n = n1 + n2

    sum_name = sum_parser['EXP']['name']
    sum_folder = ini_file.removesuffix('.ini') + os_sep + 'Summary' + os_sep + sum_name + os_sep
    data_file = sum_folder + 'all.csv'
    data = pd.read_csv(data_file)
    vary_groups = data.groupby(['Vary', 'Recommender'])\
                      .agg(LCI_95pct=pd.NamedAgg('Value', lambda x: corrected_resampled_t_statistic(x, n, n1, n2)[1][0]),
                           Value=pd.NamedAgg('Value', 'mean'),
                           UCI_95pct=pd.NamedAgg('Value', lambda x: corrected_resampled_t_statistic(x, n, n1, n2)[1][1]))
    vary_groups = vary_groups.reset_index().groupby('Vary')
    # Write Varied Experiments to xlsx
    writer = pd.ExcelWriter(sum_folder + 'vary.xlsx')
    for row, group in vary_groups:
        group.to_excel(writer, sheet_name=str(row), index=False)
    writer.save()

    def df_to_lol(df: pd.DataFrame, init=False):
        """Convert to List of Lists"""
        if init:
            return {'values': df.to_numpy().tolist(), 'headings': list(df.columns)}
        else:
            return df.to_numpy().tolist()

    def get_vary_str(vary_index):
        vary_value = varies[vary_index]
        vary_str = ''
        try:
            for vary_name in vary_config:
                vary_str += vary_name + ' = ' + str(vary_value) + '\n'
        except NameError:
            vary_str = 'No Variation'
        return vary_str
    table_headers = vary_groups.get_group(0).columns
    ci_tab = [[sg.Text('Confidence Interval Table for Value by Vary')],
              [sg.Text('Vary ' + str(0) + '    ', key='-vary-')],
              [sg.Multiline(get_vary_str(0), disabled=True, key='-vary_desc-')],
              [sg.Table(**df_to_lol(vary_groups.get_group(0), init=True), key='-table-',
                        right_click_menu=['Export', ['Export LaTeX::cTEX', 'Export CSV::cCSV', 'Nothing::cNONE']])],
              [sg.Button('<<'), sg.Button('<'), sg.Text('1   /   ' + str(n_varies), key='-status-'),
               sg.Button('>'), sg.Button('>>')]]

    ptable_headers = ['Vary', 'Recommenders', 'LCI_95pct', 'Value', 'UCI_95pct', 'p-value']
    p_tab = [[sg.Text('Compute p-value for first tab, compares up-to 3 recommenders.')],
             [sg.Text('Note: Consider using Bonferroni correction.')],
             [sg.Text('Experiment conducted using ' + str(repeats) + ' resamplings.')],
             [sg.Text('Vary ' + str(0) + '    ', key='-vary_copy-')],
             [sg.Listbox(list(group['Recommender'].unique()), key='-compare-', select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                         size=(20, 4))],
             [sg.Table([[0, '(Recommender 1, Recommender 2)', '0.0000000000', '0.00000000', '0.0000000000',
                         '0.0000000000'],
                        [0, '(Recommender 1, Recommender 3)', '0.0000000000', '0.00000000', '0.0000000000',
                         '0.0000000000'],
                        [0, '(Recommender 2, Recommender 3)', '0.0000000000', '0.00000000', '0.0000000000',
                         '0.0000000000'],
                        ],
                       headings=ptable_headers,
                       key='-ptable-',
                       max_col_width=25,
                       right_click_menu=['Export', ['Export LaTeX::pTEX', 'Export CSV::pCSV', 'Nothing::pNONE']])],
             [sg.Button('Update')]]
    tab_group = sg.TabGroup([[sg.Tab('Confidence Intervals', ci_tab),
                              sg.Tab('p-values', p_tab)]])
    layout = [[tab_group]]

    window = sg.Window('Summary Table', layout)

    def get_state(state_index: int):
        df = vary_groups.get_group(state_index)
        window['-table-'].update(df_to_lol(df))
        window['-vary-'].update('Vary ' + str(state_index))
        window['-vary_copy-'].update('Vary ' + str(state_index))
        window['-vary_desc-'].update(get_vary_str(state_index))
        window['-status-'].update(str(state_index+1) + '/' + str(n_varies))

    def get_p_table(recommenders: list, df: pd.DataFrame, vary_index: int):
        if len(recommenders) > 3:
            selected = sorted(recommenders[:3])
        else:
            selected = sorted(recommenders)
            if len(selected) < 3:
                diffs = [(0, 1)]
            else:
                diffs = [(0, 1), (0, 2), (1, 2)]
        df = df[df['Vary'] == vary_index]

        def get_diff(select: list, index_pair: tuple):
            diff_x_y = df[df['Recommender'].isin([select[index_pair[0]], select[index_pair[1]]])]\
                                           .groupby('Repeat')['Value']\
                                           .agg(lambda x: tuple(x)[0] - tuple(x)[1])
            return diff_x_y
        output_df = pd.DataFrame(columns=['Vary', 'Recommenders', 'LCI_95pct', 'Value', 'UCI_95pct', 'p-value'])
        for diff in diffs:
            diff_y_z = get_diff(selected, diff)
            p_value, confidence_interval = corrected_resampled_t_statistic(diff_y_z, n, n1, n2)
            output_df = output_df.append(
                {'Vary': vary_index,
                 'Recommenders': str((selected[diff[0]], selected[diff[1]])),
                 'LCI_95pct': confidence_interval[0],
                 'Value': np.mean(diff_y_z),
                 'UCI_95pct': confidence_interval[1],
                 'p-value': p_value}, ignore_index=True
            )
        return df_to_lol(output_df)

    def latexify(data_lol: list, headers: list):
        n_headers = len(headers)
        head = '\\begin{table}[]\n\\centering\n\\begin{tabular}{|' + 'c|' * n_headers + '}\n'
        tail = '\\end{tabular}\n\\caption{RecSearch Table}\n\\label{tab:recsearch}\n\\end{table}\n'
        output = head + '\\hline\n'
        for header in headers:
            output += '\\textbf{' + header + '} & '
        output = output[:-2] + '\\\\\n\\hline\n'
        for data_row in data_lol:
            for datum in data_row:
                output += str(datum) + ' & '
            output = output[:-2] + '\\\\\n\\hline\n'
        output += tail
        output = output.replace('_', '\\_')
        return output

    state = 0
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == '<<':
            state = 0
        if event == '<':
            if state == 0:
                state = n_varies - 1
            elif state > 0:
                state -= 1
        if event == '>>':
            state = n_varies - 1
        if event == '>':
            if state == n_varies - 1:
                state = 0
            elif state < n_varies - 1:
                state += 1
        if '>' in event or '<' in event:
            get_state(state)
        if event == 'Update' and len(compare_recommenders:=values['-compare-']) > 1:
            window['-ptable-'].update(get_p_table(compare_recommenders, data, state))
        if event == 'Export LaTeX::cTEX':
            sg.popup_scrolled(latexify(window['-table-'].get(), table_headers))
        if event == 'Export CSV::cCSV':
            sg.popup_scrolled(pd.DataFrame(window['-table-'].get(),
                                           columns=table_headers).to_csv(index=False))
        if event == 'Export LaTeX::pTEX':
            sg.popup_scrolled(latexify(window['-ptable-'].get(), ptable_headers))
        if event == 'Export CSV::pCSV':
            sg.popup_scrolled(pd.DataFrame(window['-ptable-'].get(),
                                           columns=ptable_headers).to_csv(index=False))
    window.close()


def plot_summary():
    """Plot Summary GUI"""
    sum_file = sg.popup_get_file('Select .sum file for plotting.', 'Select .sum file', file_types=(('SUM', '.sum'),))
    with open(sum_file, 'r') as file:
        sum_parser = configparser.RawConfigParser()
        sum_parser.optionxform = lambda option: option
        sum_parser.read_file(file)
    sum_name = sum_parser['EXP']['name']
    sum_experiment = sum_parser['EXP']['experiment']

    ini_file = sum_experiment
    with open(ini_file, 'r') as file:
        ini_parser = configparser.RawConfigParser()
        ini_parser.optionxform = lambda option: option
        ini_parser.read_file(file)
    try:
        vary_config = ini_parser['VARY']
        varies_base = ast.literal_eval(vary_config[list(vary_config.keys())[0]])
        varies = convert_varies_base(varies_base)
    except KeyError:
        varies = []

    sum_folder = sum_experiment.removesuffix('.ini') + os_sep + 'Summary' + os_sep + sum_name + os_sep
    data_file = sum_folder + 'all.csv'
    data = pd.read_csv(data_file)
    recommenders = sorted(list(data['Recommender'].unique()))
    column_layout = []
    for i, recommender in enumerate(recommenders):
        recommender_plot_options = [[sg.Checkbox(recommender, key='-check_rec' + str(i), default=True)],
                                    [sg.Input(recommender, key='-rec_name' + str(i), visible=False)],
                                    [sg.Text('Color:'), sg.Input('k', key='-color_rec' + str(i))],
                                    [sg.Text('Marker:'), sg.Input('$x$', key='-marker_rec' + str(i))],
                                    [sg.Text('Line Style:'), sg.Input('-', key='-ls_rec' + str(i))],
                                    [sg.Text('Label:'), sg.Input(recommender, key='-lab_rec' + str(i))],
                                    [sg.Text('Order:'), sg.Input(str(i), key='-order_rec' + str(i))],
                                    [sg.HorizontalSeparator()]]
        column_layout += recommender_plot_options
    column_layout += [[sg.Text('X-label:'), sg.Input('x', key='-xlabel-')],
                      [sg.Text('Y-label:'), sg.Input('y', key='-ylabel-')],
                      [sg.Text('Title:'), sg.Input('title', key='-title-')],
                      [sg.Text('Colormap Override:'), sg.Input(key='-colormap-')],
                      [sg.Checkbox('X-ticks at Markers', default=True, key='-xticks-')],
                      [sg.Text('X-tick Rotation:'), sg.Input('0', key='-rotation-')]]
    layout = [[sg.Column(column_layout, scrollable=True)],
              [sg.Button('Plot')]]

    window = sg.Window('Plot Experiment Summary', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Plot':
            plot_vars = {}
            if not (cm := values['-colormap-']):
                plot_vars['colormap'] = None
            else:
                plot_vars['colormap'] = cm
            plot_vars['title'] = values['-title-']
            plot_vars['xlabel'] = values['-xlabel-']
            plot_vars['ylabel'] = values['-ylabel-']

            active_recommenders = [k.removeprefix('-check_rec') for k, v in values.items() if k.startswith('-check_rec') and v]

            def active_parameter(key_prefix: str):
                parameter_prec = [(values[key_prefix + k], int(values['-order_rec' + k])) for k in active_recommenders]
                parameter_prec.sort(key=lambda x: x[1])
                active_parameters = [x[0] for x in parameter_prec]
                return active_parameters

            active_colors = active_parameter('-color_rec')
            active_markers = active_parameter('-marker_rec')
            active_ls = active_parameter('-ls_rec')
            active_labels = active_parameter('-lab_rec')
            order_recommenders = active_parameter('-rec_name')

            plt.rc('axes', prop_cycle=(
                plt.cycler('color', active_colors) +
                plt.cycler('linestyle', active_ls) +
                plt.cycler('marker', active_markers)
            ))
            plt_data = data.copy()
            if varies != []:
                plt_data['Vary'] = plt_data['Vary'].map({k: v for k, v in enumerate(varies)})
            plt_data = plt_data[plt_data['Recommender'].isin([recommenders[int(i)] for i in active_recommenders])]
            plt_data = plt_data.groupby(['Vary', 'Recommender']).agg(Value=pd.NamedAgg('Value', 'mean')).reset_index()
            plt_data = pd.pivot(plt_data, ['Recommender'], ['Vary'], ['Value'])
            plt_data.columns = plt_data.columns.get_level_values(1)
            plt_data = plt_data.T
            plt_data = plt_data[order_recommenders]
            plot = plt_data.plot(**plot_vars)
            fig = plot.get_figure()
            ax = fig.get_axes()[0]
            ax.legend(active_labels)

            if values['-xticks-']:
                ax.set_xticks(varies)
                ax.set_xticklabels(varies, rotation=values['-rotation-'])

            # Matplotlib PySimpleGUI Helper Code
            def draw_figure(canvas, figure):
                figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
                figure_canvas_agg.draw()
                figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
                return figure_canvas_agg

            plt_layout = [[sg.Text('Plot')],
                          [sg.Canvas(key='-CANVAS-')],
                          [sg.Button('Save Figure')]]

            plt_window = sg.Window('Summary Plot', plt_layout, finalize=True, element_justification='center')
            fig_canvas_agg = draw_figure(plt_window['-CANVAS-'].TKCanvas, fig)

            plt_event, plt_values = plt_window.read()
            if plt_event == 'Save Figure':
                save_file = sg.popup_get_file('Select save location:', save_as=True, file_types=(('PDF', '*.pdf'),))
                plt.savefig(save_file, bbox_inches='tight')

            plt_window.close()

    window.close()


def experiment_summary():
    """Experiment Summary Menu GUI"""
    layout = [[sg.Button('Generate Summary (SUM) Config', key='-GEN-')],
              [sg.Button('Run Summary (SUM)', key='-RUN-')],
              [sg.Button('Summary Table', key='-TAB-')],
              [sg.Button('Summary Plot', key='-PLT-')]]

    window = sg.Window('Experiment Summary', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == '-GEN-':
            call_sub_gui(generate_experiment_sum, window)
        if event == '-RUN-':
            call_sub_gui(run_experiment_sum, window)
        if event == '-TAB-':
            call_sub_gui(summary_table, window)
        if event == '-PLT-':
            call_sub_gui(plot_summary, window)

    window.close()


if __name__ == '__main__':
    experiment_summary()
