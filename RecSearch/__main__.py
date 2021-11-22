"""RecSearch Main Program"""
# Temporarily adds to sys.path to find packages/modules
import sys
from os import sep as os_sep
recsearch_directory = os_sep.join(__file__.split(os_sep)[:-2]) + os_sep
sys.path.append(recsearch_directory)
# Imports
import PySimpleGUI as sg
from RecSearch import GetProgramLocation
from RecSearch.Main.ConfigGenerator import config_generator
from RecSearch.Main.create_experiment_ini import create_experiment_ini
from RecSearch.Tools.format_data_gui import format_data_gui
from RecSearch.Tools.create_filter_file_gui import create_filter_file_gui
from RecSearch.Main.run_experiment_ini import run_experiment_ini
from RecSearch.Main.experiment_summary import experiment_summary
from RecSearch.Tests.runner import run_tests

sg.theme('SystemDefault')

layout = [[sg.Button('Generate Experiment/Base Config (CFG)', key='-CFG-')],
          [sg.Button('Generate Experiment(s) Config (INI)', key='-INI-')],
          [sg.Button('Tools', key='-TOOLS-')],
          [sg.Button('Run Experiment(s)', key='-RUN-')],
          [sg.Button('Experiment(s) Summary', key='-SUMMARY-')],
          [sg.Button('Run Tests', key='-RUNTEST-')]
          ]

window = sg.Window('RecSearch', layout)


def call_gui(func, parent_window):
    parent_window.hide()
    func()
    parent_window.un_hide()


while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == '-RUNTEST-':
        run_tests()
    if event == '-CFG-':
        call_gui(config_generator, window)
    if event == '-INI-':
        call_gui(create_experiment_ini, window)

    if event == '-TOOLS-':
        def tools_gui():
            tools_layout = [[sg.Button('Data Formatter', key='-FORMAT-')],
                            [sg.Button('Prefilter', key='-PREFILTER-')]
                            ]
            tools_window = sg.Window('RecSearch Tools', tools_layout)
            while True:
                tools_event, tools_values = tools_window.read()
                if tools_event == sg.WIN_CLOSED:
                    break
                if tools_event == '-FORMAT-':
                    call_gui(format_data_gui, tools_window)
                if tools_event == '-PREFILTER-':
                    call_gui(create_filter_file_gui, tools_window)

            tools_window.close()

        call_gui(tools_gui, window)

    if event == '-RUN-':
        call_gui(run_experiment_ini, window)
    if event == '-SUMMARY-':
        call_gui(experiment_summary, window)


window.close()
