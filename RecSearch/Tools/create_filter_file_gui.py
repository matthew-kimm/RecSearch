from RecSearch import GetProgramLocation
import PySimpleGUI as sg
from RecSearch.Tools.create_filter_file import main


def create_filter_file_gui():
    sg.theme('SystemDefault')

    layout = [[sg.Text('data [CSV] (Index, Item_History): ')],
               [sg.Input(disabled=True, key='data'), sg.FileBrowse(file_types=(('CSV', '*.csv'),), key='skip0')],
              [sg.Text('filter_file [CSV] (Course, Condition, Replace, Implies)')],
               [sg.Input(disabled=True, key='filter_file'), sg.FileBrowse(file_types=(('CSV', '*.csv'),), key='skip1')],
              [sg.Text('output_file [CSV] (Index, Filter)')],
               [sg.Input(disabled=True, key='output_file'), sg.SaveAs(file_types=(('CSV', '*.csv'),), key='skip2')],
              [sg.Button('Create')]]

    window = sg.Window('Create_Filter_File', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Create':
            params = {k: v for k, v in values.items() if 'skip' not in k}
            main(**params)
            sg.Popup('Created')

    window.close()


if __name__ == '__main__':
    create_filter_file_gui()
