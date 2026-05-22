import sys
# from imsrg_toolkit.imsrg import Imsrg
from imsrg_toolkit.kshell_utils import KshellWavefunctionScript, KshellDensityScript, KshellToolkit
from imsrg_toolkit.settings import username, ROOT_DIR
import numpy as np
import pandas as pd
import os
from pathlib import Path
import glob

def getNucl(Nucl, A):
  return f'{Nucl}{A}'


##########PARAMETERS TO CHANGE BEFORE RUN###################
kshell_log_path = f"/work/submit/{username}/results/kshell_log/outputs/"
kshell_error_path = f"/work/submit/{username}/results/kshell_log/errors/"
A =  24
Nucleus = "Al"
Nucl = getNucl(Nucleus, A)
hw = 10
opnames = ['Rp2']


vs = 'sd-shell'
state = "1+1"

snt_files = glob.glob(f"/home/submit/abelley/results/{Nucl}/SampleDelta/sd-shell_SampleDelta_*_{Nucl}_magnus_e*_E*_hw10.snt")
for snt in snt_files:
  snt_list = snt.split("/")[-1].split("_")
  SampleID = snt_list[2]
  emax = snt_list[5][1:]
  E3max = snt_list[6][1:]
  # if int(emax) < 6: continue
  fn_snt = snt
  kshell_params = {}
  kshell_params['run_cmd'] = """\
mpirun -np $SLURM_NTASKS"""
  # kshell_params['run_cmd'] = """\
  #    srun apptainer exec \\
  #      --bind /home/submit \\
  #      --bind /work/submit \\
  #      --bind /scratch/submit \\
  #      --bind /ceph/submit \\
  #      /work/submit/abelley/work/kshell/kshell.sif"""
  ###########################################################
  # If the paths dont exist, create them
  Path(kshell_log_path).mkdir(parents=True, exist_ok=True)
  Path(kshell_error_path).mkdir(parents=True, exist_ok=True)
  kshell_params['header'] = f"""#!/bin/bash
#SBATCH --job-name=test_kshell_{Nucl}_emax{emax}_Sample{SampleID}_%j
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=100
#SBATCH --time=0-01:00
#SBATCH --output={kshell_log_path}/{Nucl}_Sample_{SampleID}_e{emax}_E{E3max}_%j.txt
#SBATCH --error={kshell_error_path}/{Nucl}_Sample_{SampleID}_e{emax}_E{E3max}_%j.txt
# ulimit -s unlimited
module load mpi"""



  output_dir = f"/home/submit/abelley/results/{Nucl}/SampleDelta/"
  filebase = f"{vs}_SampleDelta_{SampleID}_{Nucl}_magnus_e{emax}_E{E3max}_hw{hw}"
  fn_ops = [f"{output_dir}{filebase}_{op}.snt" for op in opnames]


  header_expvals = f"""#SBATCH --output={kshell_log_path}/{Nucl}_Sample_{SampleID}_e{emax}_E{E3max}_%j.txt
  #SBATCH --error={kshell_error_path}/{Nucl}_Sample_{SampleID}_e{emax}_E{E3max}_%j.txt"""

  kshell = KshellToolkit(fn_snt, Nucl, [state, state], Nucl_daughter=Nucl, submit_cmd="sbatch",  **kshell_params)
  kshell.submit_all(f"{output_dir}/{filebase}_Rp2_1+.csv", fn_ops = fn_ops, ops_rankJ=[0], verbose=True,  gen_partition=True, header=header_expvals)

