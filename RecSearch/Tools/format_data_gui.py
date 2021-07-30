from RecSearch import GetProgramLocation
import PySimpleGUI as sg
from RecSearch.Tools.format_data import main


def format_data_gui():
    sg.theme('SystemDefault')

    layout = [[sg.Text('attribute_data [CSV] (Index, Attribute Columns ...): ')],
               [sg.Input(disabled=True, key='attribute_csv'), sg.FileBrowse(file_types=(('CSV', '*.csv'),), key='skip0')],
              [sg.Text('item_history_data [CSV] (Index, Item, Rating)')],
               [sg.Input(disabled=True, key='item_history_csv'), sg.FileBrowse(file_types=(('CSV', '*.csv'),), key='skip1')],
              [sg.Text('target_coded_term (Target term and greater are used for recommendation,'
                       'prior to target term for history)')],
              [sg.Input('2', key='target_term')],
              [sg.Text('output_file [CSV] (Index, Item_History, Item_Rating, Attributes ...)')],
               [sg.Input(disabled=True, key='output_file'), sg.SaveAs(file_types=(('CSV', '*.csv'),), key='skip2')],
              [sg.Button('Format Data')]]

    window = sg.Window('Format_Data', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Format Data':
            params = {k: v for k, v in values.items() if 'skip' not in k}
            main(**params)
            sg.Popup('Formatted')

    window.close()


if __name__ == '__main__':
    format_data_gui()
