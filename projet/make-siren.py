####################################################################################################

from FinancialSimulator.IdentificationNumber import *
from FinancialSimulator.IdentificationNumber.LuhnChecksum import *

siren = append_luhn_checksum(32165497)
siret = make_siret(siren, 1)
vat = make_fr_vat(siren)

print('SIREN:', format_siren(siren))
print('SIRET:', format_siret(siret))
print('TVA:', vat)

bban = make_bban(20041, 1012, '4342989F033')
# checksum = 54
print('BBAN:', bban)
iban = make_iban('FR', bban)
print('IBBAN:', iban)
print(check_iban(iban))
