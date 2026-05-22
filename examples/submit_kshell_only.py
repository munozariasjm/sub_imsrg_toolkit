import sys
# from imsrg_toolkit.imsrg import Imsrg
from imsrg_toolkit.kshell_utils import KshellWavefunctionScript, KshellDensityScript, KshellToolkit
from imsrg_toolkit.utils import Utils
import numpy as np
import pandas as pd
import glob

Nucl = "Al22"

snt_files = glob.glob(f"/home/submit/abelley/results/Al22/SampleDelta/sd-shell_SampleDelta_*_Al22_magnus_e*_E*_hw10.snt")

for snt in snt_files[0]:
  snt_list = snt.split("/")[-1].split("_")
  SampleID = snt_list[3]
  emax = snt_list[5][1:]
  E3max = snt_list[6][1:]

  imsrg_params = {}
  imsrg_params['emax'] = emax
  imsrg_params['E3max'] = E3max
  imsrg_params['hw'] = 10
  imsrg_params['A'] = 22
  imsrg_params['opnames'] = ['Rp2']
  imsrg_params['ref'] = Nucl
  imsrg_params['valence_space'] = 'sd-shell' # this is just a label when custom_valence_space is set
  imsrg_params['label'] = 'SampleDelta'

  kshell_params = {}
  kshell_params['run_cmd'] = """\
    srun apptainer exec \\
      --bind /home/submit \\
      --bind /work/submit \\
      --bind /scratch/submit \\
      --bind /cvmfs \\
      --bind /ceph/submit \\
      /work/submit/abelley/work/kshell/kshell.sif """
  kshell_params['header'] = f"""#!/bin/bash
  #SBATCH --job-name=kshell
  #SBATCH --nodes=1
  #SBATCH --ntasks=1
  #SBATCH --cpus-per-task=10
  #SBATCH --output=/work/submit/abelley/results/kshell_log/outputs/{imsrg_params['ref']}_emax{imsrg_params['emax']}%j.txt
  #SBATCH --error=/work/submit/abelley/results/kshell_log/errors/{imsrg_params['ref']}_emax{imsrg_params['emax']}_%j.txt
  #SBATCH --time=30:00 """




  header_expvals = f"""#SBATCH --output=/work/submit/abelley/results/kshell_log/outputs/{imsrg_params['ref']}_emax{imsrg_params['emax']}_Sample{SampleID}_eval_%j.txt
  # #SBATCH --error=/work/submit/abelley/results/kshell_log/errors/{imsrg_params['ref']}_emax{imsrg_params['emax']}_Sample{SampleID}_eval_%j.txt"""

  imsrg_submit = Utils(Nucl, ["1+1", "1+1"], imsrg_params, kshell_params)
    
  fn_ops = [f"{imsrg_submit.output_dir}{imsrg_submit.filebase}_{op}.snt" for op in imsrg_submit.opnames]
  tmp = [f"{imsrg_submit.output_dir}{imsrg_submit.filebase}_{op[1]}.snt" for op in imsrg_submit.opfiles]
  fn_ops.extend(tmp)
  imsrg_submit.kshell.submit_all(f"{imsrg_submit.output_dir}/{imsrg_submit.filebase}_ops.csv", fn_ops,  ops_rankJ = [0],  verbose=True, header=header_expvals, gen_partition=True)