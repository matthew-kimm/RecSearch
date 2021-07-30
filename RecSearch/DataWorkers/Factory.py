import importlib
from RecSearch.ExperimentSupport.ExperimentData import ExperimentData


class UserDataWorkerError(Exception):
    """Exception raised for user created data workers."""
    def __init__(self, message: str, data_worker_folder: str, data_worker_file: str):
        self.message = message + " in module " + data_worker_file + ' in package ' + data_worker_folder + '.'


class UserNamingError(UserDataWorkerError):
    """Exception for not finding Data Worker."""
    def __init__(self, data_worker_folder: str, data_worker_file: str):
        super("No class named ' + data_worker_file + ' (data worker class must shared name with its module) ",
              data_worker_folder, data_worker_file)


class DataWorkerFactory:
    @staticmethod
    def get_data_worker(data_worker: str, name: str, data_worker_config: dict, Data: ExperimentData):
        data_worker_folder = 'RecSearch.DataWorkers'
        module = importlib.import_module('.'+data_worker, data_worker_folder)
        DataWorkerClasses = [class_name for class_name in dir(module) if class_name == data_worker]
        if len(DataWorkerClasses) == 1:
            DataWorkerClass = getattr(module, DataWorkerClasses[0])
            return DataWorkerClass(name, data_worker_config, Data)
        elif len(DataWorkerClasses) > 1:
            # Not possible to have two identically named classes?
            raise NotImplementedError
        else:
            raise UserNamingError(data_worker_folder, data_worker)
