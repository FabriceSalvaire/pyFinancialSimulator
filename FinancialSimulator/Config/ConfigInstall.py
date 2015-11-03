####################################################################################################

import os

####################################################################################################

import FinancialSimulator.Tools.Path as PathTools # due to Path class

####################################################################################################

_file_path = PathTools.to_absolute_path(__file__)
_config_module_path = os.path.dirname(_file_path)

_module_path = PathTools.parent_directory_of(_config_module_path)

# Fixme: wrong when installed
_source_directory = PathTools.parent_directory_of(_module_path)
_share_directory = os.path.join(_source_directory, 'share')

class Path:

    module_path = _module_path
    share_directory = _share_directory
    config_directory = os.path.join(share_directory, 'config')
    accounting_data_directory = os.path.join(share_directory, 'accounting')

####################################################################################################

class Logging:

    default_config_file = 'logging.yml'
    directories = (Path.config_directory,)

    ##############################################

    @staticmethod
    def find(config_file):

        return PathTools.find(config_file, Logging.directories)

####################################################################################################
#
# End
#
####################################################################################################
