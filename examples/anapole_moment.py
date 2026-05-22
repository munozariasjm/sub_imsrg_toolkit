import sys
# from imsrg_toolkit.imsrg import Imsrg
from imsrg_toolkit.kshell_utils import KshellWavefunctionScript, KshellDensityScript, KshellToolkit
from imsrg_toolkit.utils import Utils
from imsrg_toolkit.settings import username
import numpy as np
import pandas as pd

#for O14
#emax=4 can request 10min with 1G and it is more than enough
#emax=6 can request 15min with 4G
#emax=8 can request 2:00 with 20G
#emax=10 can request 10:00:00 with 100G

opfiles_path = "/work/submit/abelley/operators"

##########PARAMETERS TO CHANGE BEFORE RUN###################
emax = [1,2,3,4,5,6,7,8,9,10]
time = ["00:10:00", "00:10:00","00:10:00","00:10:00","00:10:00","00:30:00","01:00:00", "02:00:00","06:00:00","08:00:00"]
memory = ['10G','10G','10G','10G','10G','10G', "10G", '20G', "20G",'60G',"100G"]
# vs = 'p-shell'
# mass =  [9, 13, 14, 15]
# Nuclei = ["Be", "C", "N", "N"]
# states = ["1.5-1", "0.5-1", "1+1", "0.5-1"]
# emax = [2,3,4,5,6,7,8,9,10]
# time = ["00:10:00","00:10:00","00:10:00","00:10:00","00:30:00","01:00:00", "02:00:00","06:00:00","08:00:00"]
# memory = ['10G','10G','10G','10G','10G', "10G", '20G', "20G",'60G',"100G"]
vs = 'sd-shell'
# mass =  [25, 29]
# Nuclei = ["Mg", "Si"]
# states = ["2.5+1", "0.5+1"]
mass =  [29]
Nuclei = ["Si"]
states = ["0.5+1"]

file2b = "TwBME-HO_NN-only_N3LO_EM500_srg2.0_hw16_emax16_e2max32.me2j.gz"
file3b = "NO2B_ThBME_srg2.0_ramp46_N3LO_EM500_JJmax13_c1_-0.81_c3_-3.2_c4_5.4_cD_0.7_cE_-0.06_LNL2_650_500_IS_hw16from30_ms18_36_24.stream.bin"
###########################################################


def getNucl(Nucl, A):
  return f'{Nucl}{A}'
for Nucleus, A, state in zip(Nuclei, mass, states):
  for e, t, m in zip(emax,time, memory):
    Nucl = getNucl(Nucleus, A)
    if 3*e < 24:
      E3max = 3*e
    else:
      E3max = 24
    for BCM in [0.0, 1.0, 2.0]:
      print(f"Running {Nucl} emax={e} E3max={E3max} BCM={BCM}")
      imsrg_params = {}
      imsrg_params['emax'] = e
      imsrg_params['E3max'] = E3max
      imsrg_params['hw'] = 16
      imsrg_params['A'] = A
      imsrg_params['ref'] = Nucl
      imsrg_params['valence_space'] = vs # this is just a label when custom_valence_space is set
      imsrg_params['label'] = 'N3LO_lnl'
      imsrg_params['BetaCM'] = BCM
      imsrg_params['hwBetaCM'] = 16
      imsrg_params['file2e1max'] = 16
      imsrg_params['file2e2max'] = 32
      imsrg_params['file2lmax'] = 16
      imsrg_params['file3e1max'] = 18
      imsrg_params['file3e2max'] = 36
      imsrg_params['file3e3max'] = 24
      imsrg_params['file3_precision'] = 'full'
      imsrg_params['run_cmd'] = """\
srun apptainer exec \\
  --bind /home/submit \\
  --bind /work/submit \\
  --bind /scratch/submit \\
  --bind /ceph/submit \\
  /work/submit/abelley/imsrg/pyimsrg.sif """
#     imsrg_params['run_cmd'] = """\
# srun apptainer exec \\
#   --bind /home/submit \\
#   --bind /work/submit \\
#   --bind /scratch/submit \\
#   --bind /ceph/submit \\
#   /work/submit/abelley/imsrg/pyimsrg.sif """

      kshell_params = {}
      kshell_params['scratch_directory'] = f"/work/submit/{username}/work/kshell/"
#       kshell_params['run_cmd'] = """
# mpirun -np $SLURM_NTASKS """
      kshell_params['run_cmd'] = """
srun """
      kshell_params['header'] = f"""#!/bin/bash
#SBATCH --job-name=kshell_{Nucl}_emax{e}_{imsrg_params['label']}_%j
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=10
#SBATCH --mem-per-cpu=1000M
#SBATCH --time=0-01:00
# ulimit -s unlimited
module load mpi"""


      imsrg_params['header'] = f"""#!/bin/bash
#SBATCH --job-name={imsrg_params['ref']}_emax{imsrg_params['emax']}_magic_%j
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --output=/work/submit/abelley/results/imsrg_log/outputs/{imsrg_params['ref']}_emax{imsrg_params['emax']}_{imsrg_params['label']}_%j.txt
#SBATCH --error=/work/submit/abelley/results/imsrg_log/errors/{imsrg_params['ref']}_emax{imsrg_params['emax']}_{imsrg_params['label']}_%j.txt
#SBATCH --time={t}
#SBATCH --mem={m}

cd $SLURM_SUBMIT_DIR
export OMP_NUM_THREADS=24"""



      header_expvals = f"""#SBATCH --output=/work/submit/abelley/results/kshell_log/outputs/{imsrg_params['ref']}_emax{imsrg_params['emax']}_{imsrg_params['label']}_eval_%j.txt
#SBATCH --error=/work/submit/abelley/results/kshell_log/errors/{imsrg_params['ref']}_emax{imsrg_params['emax']}_{imsrg_params['label']}_eval_%j.txt"""

      imsrg_submit = Utils(Nucl, [state, state], imsrg_params, kshell_params)
      imsrg_submit.submit_all_anapole(file2b, file3b, f"{imsrg_submit.output_dir}/{imsrg_submit.filebase}_anapole.csv", header_expvals = header_expvals, verbose=True, ops_rankJ=[1], staged = False)
      # fn_ops = fn_ops = [f"{imsrg_submit.output_dir}{imsrg_submit.filebase}_Anapolepp.snt"]
      # imsrg_submit.kshell.submit_anapole(f"{imsrg_submit.output_dir}/{imsrg_submit.filebase}_anapole.csv", fn_ops,  ops_rankJ = [1],  verbose=True, scale=1000, header=header_expvals)
    # count +=1 