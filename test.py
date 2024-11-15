import sys
from imsrg_toolkit.utils import imsrg_toolkit



params = {}
params['emax'] = 4
params['E3max'] = 12
params['hw'] = 16
params['A'] = 6
params['opnames'] = ['Rp2']
params['ref'] = "He6"
params['valence_space'] = 'p-shell' # this is just a label when custom_valence_space is set

imsrg = imsrg_toolkit()
imsrg.update_params(**params)
imsrg.run('TwBME-HO_NN-only_N3LO_EM500_srg1.80_hw16_emax18_e2max36.me2j.gz',
          'NO2B_half_ThBME_EM1.8_2.0_3NFJmax15_IS_hw16_ms16_32_28.stream.bin')