"""
Importing this sets the working directory appropriately.
Sets the working directory to the program directory (where this file is located).
Required for finding DataWorkers/DataInterfaces.
"""
from os import sep as os_sep
from os import chdir

# Global
recsearch_directory = __file__
recsearch_directory = os_sep.join(recsearch_directory.split(os_sep)[:-1])
chdir(recsearch_directory)
