"""
Defines functions for creating input elements with consistent key naming.
"""
import PySimpleGUI as sg
import ast
from RecSearch.Config.ConfigValidator import default_validator
from RecSearch.Config.ConfigGenKeyManage import KeyManager


class InputFunctions:
    """
    Manages input function definitions for calling.
    """
    def __init__(self, add_functions: dict = None):
        self.validator = default_validator
        self.functions = {
            'text': text,
            'neighborhood': neighborhood,
            'column': column,
            'columns': columns,
            'methods': methods,
            'recommender': recommender,
            'file': file,
            'filters': filters,
            'metric': metric,
            'metric_recommender': metric_recommender,
        }
        if add_functions is not None:
            self.functions.update(add_functions)

    def call_input(self, input_func: str, param: str, check: str, base_key: str, key_manager: KeyManager) -> list:
        """
        Parse input function string from class attribute cfg[...]['input'] to call function with arguments
         for creating a PySimpleGUI layout row.
        :param input_func: python style function call for input function. e.g. 'text()'
         Supports positional arguments and keyword arguments e.g. 'text(disabled=True)'
        :param param: name of parameter
        :param check: check string for parameter
        :param base_key: the base_key for the parameter :Worker/Interface:Required/Optional:dw(:di)
        :param key_manager: pass the default key manager (adds keys to manager for each new input element)
        :return:
        """
        # Abstract Syntax Tree Parsing of Function and Positional/Keyword Arguments to adjust function call
        ast_body, = ast.parse(input_func).body
        func = ast_body.value.func.id
        args = []
        for arg in ast_body.value.args:
            args.append(arg.value)
        kwargs = {kwarg.arg: kwarg.value for kwarg in ast_body.value.keywords}
        default_value = None
        try:
            default_value = self.validator.get_default_value(check)
        except KeyError:
            pass
        kwargs.update({'param': param})
        kwargs.update({'default_value': default_value})
        kwargs.update({'base_key': base_key})
        kwargs.update({'key_manager': key_manager})
        func = self.functions[func]
        return func(*args, **kwargs)


def get_param_key(base_key: str, param: str, update_type: str = '') -> str:
    """Get the GUI parameter key to be used for input elements"""
    return update_type + base_key + ':' + param


def change_default_type_if_none(default_value, new_type):
    """For GUI elements whose values come from a list, default can not be None"""
    if default_value is None:
        return new_type
    else:
        return default_value


# START ROW ELEMENTS
# ---------------------
def check_help_buttons(param_key: str, key_manager: KeyManager) -> list:
    """
    Create Check/Help buttons for input
    :param param_key: GUI key for the parameter
    :param key_manager: default key manager (adds keys of the buttons to the key manager)
    :return:
    """
    button_elements = [sg.Button('Check', key=(check_key := param_key + ':Check')),
                       sg.Button('Help', key=(help_key := param_key + ':Help'))]
    key_manager.update_param_keys([check_key, help_key])
    return button_elements


def tag(param: str) -> list:
    """Text label to appear before input element"""
    text_element = [sg.Text(param), ]
    return text_element


def text_box(param: str, default_value: str, base_key: str, key_manager: KeyManager, disabled: bool = False) -> list:
    """Input (textbox) element"""
    input_element = [sg.Input(default_value, key=(param_key := get_param_key(base_key, param)), disabled=disabled), ]
    key_manager.update_param_keys([param_key])
    input_element += check_help_buttons(param_key, key_manager)
    return input_element


def file_box(param: str, default_value: str, base_key: str, key_manager: KeyManager) -> list:
    """File input box element"""
    file_element = [sg.Input(default_value, key=(param_key := get_param_key(base_key, param)), disabled=True),
                    sg.FileBrowse()]
    key_manager.update_param_keys([param_key])
    file_element += check_help_buttons(param_key, key_manager)
    return file_element


def file_check_box(param: str, base_key: str) -> list:
    file_check_box_element = [sg.Checkbox('Rel Path', key=get_param_key(base_key, param, '&Rel&'), enable_events=True),]
    return file_check_box_element


def combo_box(param: str, default_value, base_key: str, key_manager: KeyManager, update_type: str = '',
              events: bool = False, disabled: bool = False) -> list:
    """Combo box element"""
    combo_size = (20, 10)
    combo_element = [sg.Combo(default_value,
                              key=(param_key := get_param_key(base_key, param, update_type)),
                              size=combo_size, enable_events=events, disabled=disabled), ]
    combo_element += check_help_buttons(param_key, key_manager)
    if update_type:
        key_manager.update_types([update_type])
    key_manager.update_param_keys([param_key])
    return combo_element


def list_box(param: str, default_value, base_key: str, key_manager: KeyManager, update_type: str = '',
             select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED) -> list:
    """Listbox element"""
    list_size = (20, 10)
    list_element = [sg.Listbox(default_value,
                               key=(param_key := get_param_key(base_key, param, update_type)),
                               size=list_size,
                               select_mode=select_mode), ]
    list_element += check_help_buttons(param_key, key_manager)
    if update_type:
        key_manager.update_types([update_type])
    key_manager.update_param_keys([param_key])
    return list_element
# ___________________
# END ROW ELEMENTS


# START ROW OF ELEMENTS
# ------------------
def text_row(param: str, default_value: str, base_key: str, key_manager: KeyManager, disabled: bool = False) -> list:
    """Tag, Textbox, Check/Help Buttons"""
    row = tag(param) + text_box(param, default_value, base_key, key_manager, disabled)
    return row


def file_row(param: str, default_value: str, base_key: str, key_manager: KeyManager) -> list:
    """Tag, Textbox, FileBrowse Button, Check/Help Buttons"""
    row = tag(param) + file_box(param, default_value, base_key, key_manager)
    return row


def combo_row(param: str, default_value: str, base_key: str, key_manager: KeyManager, update_type: str = '',
              events: bool = False, disabled: bool = False) -> list:
    """Tag, Combobox, Check/Help Buttons"""
    default_value = change_default_type_if_none(default_value, [])
    row = tag(param) + combo_box(param, default_value, base_key, key_manager, update_type, events, disabled)
    return row


def listbox_row(param: str, default_value: str, base_key: str, key_manager: KeyManager, update_type: str = '',
                select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED) -> list:
    """Tag, Listbox, Check/Help Buttons"""
    default_value = change_default_type_if_none(default_value, [])
    row = tag(param) + list_box(param, default_value, base_key, key_manager, update_type, select_mode)
    return row
# ________________
# END ROW OF ELEMENTS


# START INPUT DEFINITIONS
# -----------------------
def text(param: str, default_value: str, base_key: str, key_manager: KeyManager, disabled: bool = False) -> list:
    """Input textbox for parameter"""
    row = text_row(param, default_value, base_key, key_manager, disabled)
    return row


def file(param: str, default_value: str, base_key: str, key_manager: KeyManager) -> list:
    """File selector for parameter"""
    row = [sg.Column([file_row(param, default_value, base_key, key_manager), file_check_box(param, base_key)]),]
    return row


def neighborhood(param: str, default_value: str, base_key: str, key_manager: KeyManager) -> list:
    """Neighborhood combo box selector for parameter"""
    update_type = '|neighborhood|'
    row = combo_row(param, default_value, base_key, key_manager, update_type)
    return row


def filters(param: str, default_value: str, base_key: str, key_manager: KeyManager) -> list:
    """Filter combo box selector for parameter"""
    update_type = '|filters|'
    row = combo_row(param, default_value, base_key, key_manager, update_type)
    return row


def column(param: str, default_value: str, base_key: str, key_manager: KeyManager) -> list:
    """Column combo box selector for parameter"""
    update_type = '|column|'
    row = combo_row(param, default_value, base_key, key_manager, update_type)
    return row


def columns(param: str, default_value: str, base_key: str, key_manager: KeyManager) -> list:
    """Columns listbox selector for parameter"""
    update_type = '|column|'
    row = listbox_row(param, default_value, base_key, key_manager, update_type)
    return row


def methods(param: str, default_value: str, base_key: str, key_manager: KeyManager) -> list:
    """Combo box selector for interface parameter of dataworker"""
    row = combo_row(param, default_value, base_key, key_manager, events=True)
    return row


def recommender(param: str, default_value: str, base_key: str, key_manager: KeyManager) -> list:
    """Recommender listbox selector for parameter"""
    update_type = '|recommender|'
    row = listbox_row(param, default_value, base_key, key_manager, update_type)
    return row


def metric(param: str, default_value: str, base_key: str, key_manager: KeyManager) -> list:
    """Metric combo box selector for parameter"""
    update_type = '|metric|'
    row = combo_row(param, default_value, base_key, key_manager, update_type, events=True)
    return row


def metric_recommender(param: str, default_value: str, base_key: str, key_manager: KeyManager) -> list:
    """Combo box for recommenders associated with a specific metric"""
    update_type = '|metric_recommender|'
    row = combo_row(param, default_value, base_key, key_manager, update_type, disabled=True)
    return row
# _____________________
# END INPUT DEFINITIONS
