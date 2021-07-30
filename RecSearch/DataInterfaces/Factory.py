import importlib


class UserInterfaceError(Exception):
    """Exception raised for user created interfaces."""
    def __init__(self, message: str, interface_folder: str, interface_file: str):
        self.message = message + " in module " + interface_file + ' in package ' + interface_folder + '.'


class UserNamingError(UserInterfaceError):
    """Exception for not finding an implemented interface starting with IX."""
    def __init__(self, interface_folder: str, interface_file: str):
        super().__init__("No class starting with IX (implemented interfaces must start with IX to be recognized) ",
              interface_folder, interface_file)


class UserFormatError(UserInterfaceError):
    """Exception for multiple implemented interfaces starting with IX in a file."""
    def __init__(self, interface_folder: str, interface_file: str):
        super().__init__("More than one class starting with IX (only one implemented interface per file) ",
              interface_folder, interface_file)


class InterfaceFactory:
    @staticmethod
    def get_interface(interface_folder: str, interface_file: str):
        module = importlib.import_module('.' + interface_file, 'RecSearch.DataInterfaces.' + interface_folder)
        IXinterface = [name for name in dir(module) if name.startswith('IX')]
        if len(IXinterface) == 1:
            IXClass = getattr(module, IXinterface[0])
            return IXClass()
        elif len(IXinterface) > 1:
            raise UserFormatError(interface_folder, interface_file)
        else:
            raise UserNamingError(interface_folder, interface_file)
