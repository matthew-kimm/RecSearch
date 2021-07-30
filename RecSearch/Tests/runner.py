import RecSearch.GetProgramLocation
import unittest
import glob
import importlib
from os import chdir, sep

chdir('.' + sep + 'Tests' + sep)
# import test modules
test_module_all_paths = glob.glob('*' + sep + '**' + sep + '*.py')
test_module_paths = [path for path in test_module_all_paths if path.split(sep)[-1].startswith('Test_')]
# change [:-3] to .removesuffix('.py') once update to Python 3.9
test_module_names = ['RecSearch.Tests.' + name.replace(sep, '.')[:-3] for name in test_module_paths]
test_module_tuple = [('.'.join(name.split('.')[:-1]), '.' + name.split('.')[-1]) for name in test_module_names]
test_modules = [importlib.import_module(mname, pname) for pname, mname in test_module_tuple]

# initialize the test suite
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# add tests to the test suite
for test in test_modules:
    suite.addTests(loader.loadTestsFromModule(test))

#initialize a runner, pass it the test suite and run
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
