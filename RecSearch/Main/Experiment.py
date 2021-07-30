import RecSearch.GetProgramLocation
from RecSearch.ExperimentSupport.ExperimentData import ExperimentData
from RecSearch.ExperimentSupport.ExperimentParameters import ExperimentParameters
from RecSearch.DataWorkers.Factory import DataWorkerFactory
from os import sep as os_sep


class Experiment:
    """
    Experiment class conducts an experiment.
    """
    def __init__(self, configfile: str, load: bool = False):
        self.experiment_name = configfile.split(os_sep)[-1].removesuffix('.cfg')
        self.experiment_folder = os_sep.join(configfile.split(os_sep)[:-1])
        self.ExpPar = ExperimentParameters(configfile)
        if load:
            self.ExpData = ExperimentData(configfile, self.ExpPar.cfg()['DATA'], load_experiment=True)
        else:
            self.ExpData = ExperimentData(configfile, self.ExpPar.cfg()['DATA'], self.ExpPar.cfg()['DW_Splitters']['Default'])
        self.DataDriver = DataDriver(self.ExpData, self.ExpPar)

    def run(self):
        self.DataDriver.run()


class DataDriver:
    """
    DataDriver class drives the operations that add to the data.
    """
    def __init__(self, Data: ExperimentData, Config: ExperimentParameters):
        self.Data = Data
        self.Config = Config
        self.exclude = ['DW_Splitters']

        self.DataWorkerCfgs = {k.removeprefix('DW_'): v for k, v in self.Config.cfg().items()
                               if k.startswith('DW_')
                               and k not in self.exclude}
        self.DataWorkerOrder = [t[0] for t in
                                sorted(self.DataWorkerCfgs.items(), key=lambda dict_tup: dict_tup[1]['precedence'])]
        # Strip Non-Second Level Configs
        self.DataWorkerCfgs = {k: {name: cfg_dict for name, cfg_dict in top.items() if isinstance(cfg_dict, dict)}
                               for k, top in self.DataWorkerCfgs.items()}
        self.DataWorkers = []
        for DW_key in self.DataWorkerOrder:
            for name, DataWorkerCfg in self.DataWorkerCfgs[DW_key].items():
                self.DataWorkers.append(DataWorkerFactory.get_data_worker(DW_key, name, DataWorkerCfg, self.Data))

    def run(self):
        """
        Run through experiment saving columns once computed, if column already exists (from loading) skip that column
        :return:
        """
        # New recommendation method flag resets Metrics and Comparers
        new_rec_flag = False
        for DataWorker in self.DataWorkers:
            cname = DataWorker.get_column_name()
            print(cname)
            eval_columns = self.Data.get_dataset(self.Data.get_eval_data())
            if cname.startswith('M__') or cname.startswith('C__'):
                if len(reset_columns := [col for col in eval_columns if col.startswith(cname)]) > 0:
                    if new_rec_flag:
                        self.Data.reset(reset_columns)
                    else:
                        continue
            else:
                if cname in eval_columns:
                    continue
                else:
                    if cname.startswith('R__'):
                        new_rec_flag = True
            DataWorker.do_the_work()
            self.Data.save_data()
