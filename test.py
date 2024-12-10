import sys
# from imsrg_toolkit.imsrg import Imsrg
from imsrg_toolkit.kshell_utils import KshellWavefunctionScript, KshellDensityScript, KshellToolkit
from imsrg_toolkit.utils import Utils
import numpy as np



imsrg_params = {}
imsrg_params['emax'] = 2
imsrg_params['E3max'] = 6
imsrg_params['hw'] = 10
imsrg_params['A'] = 6
imsrg_params['opnames'] = ['Rp2']
imsrg_params['ref'] = "He6"
imsrg_params['valence_space'] = 'p-shell' # this is just a label when custom_valence_space is set
imsrg_params['label'] = 'SampleDelta'
imsrg_params['header'] = """#!/bin/bash
#SBATCH --job-name=test
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --output=/work/submit/abelley/results/imsrg_log/outputs/test_out_%j.txt
#SBATCH --error=/work/submit/abelley/results/imsrg_log/errors/test_err_%j.txt
#SBATCH --time=10:00

cd $SLURM_SUBMIT_DIR
export OMP_NUM_THREADS=24
"""
imsrg_params['run_cmd'] = """\
  srun apptainer exec \\
    --bind /home/submit \\
    --bind /work/submit \\
    --bind /scratch/submit \\
    --bind /cvmfs \\
    --bind /ceph/submit \\
    /work/submit/abelley/pyimsrg.sif """
LECs = [-0.3561991764052598,-0.3551422338060104,-0.3499850422217293,-0.24815714578728915,2.787629818761447,0.4330970444321269,-0.0867054439310162,-1.2993292484597436,0.7880004196842763,0.5200889706434243,-0.8462647684441067,-0.7366737819891919,-0.6069157859201317,-0.4789800999145507,0.9303137685739377,-0.5882855441685089,-0.06894355986916434]


kshell_params = {}
kshell_params['path_to_kshell'] = "/work/submit/abelley/kshell-20230714-ver4/src"
kshell_params['run_cmd'] = """\
  srun apptainer exec \\
    --bind /home/submit \\
    --bind /work/submit \\
    --bind /scratch/submit \\
    --bind /cvmfs \\
    --bind /ceph/submit \\
    /work/submit/abelley/work/kshell/kshell.sif """
kshell_params['header'] = """#!/bin/bash
#SBATCH --job-name=test
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --output=/work/submit/abelley/results/kshell_log/outputs/test_out_%j.txt
#SBATCH --error=/work/submit/abelley/results/kshell_log/errors/test_err_%j.txt
#SBATCH --time=10:00 """

header_expvals = """#SBATCH --output=/work/submit/abelley/results/kshell_log/outputs/test_out_%j.txt
# #SBATCH --error=/work/submit/abelley/results/kshell_log/errors/test_err_%j.txt"""

imsrg_submit = Utils("He6", ["+1", "+1"], imsrg_params, kshell_params)
# imsrg_submit.submit_imsrg("TwBME-HO_NN-only_N3LO_EM500_srg1.80_hw16_emax18_e2max36.me2j.gz","NO2B_half_ThBME_EM1.8_2.0_3NFJmax15_IS_hw16_ms16_32_28.stream.bin", verbose=True)
# imsrg_submit.submit_imsrg_combine_delta(LECs, 2007, verbose=True)
imsrg_submit.submit_all("TwBME-HO_NN-only_N3LO_EM500_srg1.80_hw16_emax18_e2max36.me2j.gz",
  "NO2B_half_ThBME_EM1.8_2.0_3NFJmax15_IS_hw16_ms16_32_28.stream.bin", 
  verbose=True, header_expvals = header_expvals)



# params = {}
# params['path_to_kshell'] = "/work/submit/abelley/kshell-20230714-ver4/src"
# params['run_cmd'] = """\
#   srun apptainer exec \\
#     --bind /home/submit \\
#     --bind /work/submit \\
#     --bind /scratch/submit \\
#     --bind /cvmfs \\
#     --bind /ceph/submit \\
#     /work/submit/abelley/work/kshell.sif """
# # params['run_cmd'] = 'srun'

# params['header'] = """#!/bin/bash
# #SBATCH --job-name=test
# #SBATCH --nodes=1
# #SBATCH --ntasks=1
# #SBATCH --cpus-per-task=10
# #SBATCH --output=/work/submit/abelley/results/kshell_log/outputs/test_out_%j.txt
# #SBATCH --error=/work/submit/abelley/results/kshell_log/errors/test_err_%j.txt
# #SBATCH --time=10:00 """


# header_calexpval = """#SBATCH --output=/work/submit/abelley/results/kshell_log/outputs/test_out_%j.txt
# #SBATCH --error=/work/submit/abelley/results/kshell_log/errors/test_err_%j.txt"""

# he6_wf = kshell_wavefunction_script("/work/submit/abelley/results/He6/SampleDelta/p-shell_SampleDelta_2007_He6_magnus_e2_E6_hw16.snt")
# he6_wf.update_params(**params)
# # he6_wf.gen_partition(1)
# he6_wf.gen_script(gen_partition=True)

# params = {}
# params['path_to_kshell'] = "/work/submit/abelley/kshell-20230714-ver4/src"

# he6_density = kshell_density_script("/work/submit/abelley/results/He6/SampleDelta/p-shell_SampleDelta_2007_He6_magnus_e2_E6_hw16.snt")
# he6_density.update_params(**params)
# he6_density.gen_script("/work/submit/abelley/work/He6_p-shell_SampleDelta_2007_He6_magnus_e2_E6_hw16_p.ptn")

# he6 = KshellToolkit("/work/submit/abelley/results/He6/SampleDelta/p-shell_SampleDelta_2007_He6_magnus_e2_E6_hw16.snt", "He6", ["+1", "+1"], **params)
# he6.calc_opexpvals("/work/submit/abelley/results/He6/SampleDelta/p-shell_SampleDelta_2007_He6_magnus_e2_E6_hw16_Rp2.snt")
# he6.calc_opexpvals("/work/submit/abelley/results/He6/SampleDelta/p-shell_SampleDelta_2007_He6_magnus_e2_E6_hw16_Rp2_HF.snt")
# he6.gen_df_from_outputs()
# print(he6.df)
# he6.gen_expvals_script(['/work/submit/abelley/results/He6/SampleDelta/p-shell_SampleDelta_2007_He6_magnus_e2_E6_hw16_Rp2.snt', '/work/submit/abelley/results/He6/SampleDelta/p-shell_SampleDelta_2007_He6_magnus_e2_E6_hw16_Rp2_HF.snt'])
# he6.submit_all('/work/submit/abelley/results/He6/test_output.csv', ['/work/submit/abelley/results/He6/SampleDelta/p-shell_SampleDelta_2007_He6_magnus_e2_E6_hw16_Rp2.snt', '/work/submit/abelley/results/He6/SampleDelta/p-shell_SampleDelta_2007_He6_magnus_e2_E6_hw16_Rp2_HF.snt'], verbose= True)

