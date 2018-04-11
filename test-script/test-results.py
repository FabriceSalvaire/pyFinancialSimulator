####################################################################################################

import FinancialSimulator.Logging.Logging as Logging

logger = Logging.setup_logging('financial-simulator')
_module_logger = logger

####################################################################################################

from FinancialSimulator.Accounting import Results

####################################################################################################

# yaml_file = 'systeme-abrege-resultat-tableau.yml'
yaml_file = 'systeme-base-bilan-tableau.yml'
# yaml_file = 'test.yml' # FAIL !!!
yaml_loader = Results.YamlLoader(yaml_file)
table = yaml_loader.table
