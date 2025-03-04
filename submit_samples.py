import sys
# from imsrg_toolkit.imsrg import Imsrg
from imsrg_toolkit.kshell_utils import KshellWavefunctionScript, KshellDensityScript, KshellToolkit
from imsrg_toolkit.utils import Utils
import numpy as np
import pandas as pd

#for O14
#emax=4 can request 2min with 256M and it is more than enough
#emax=6 can request 15min with 2G
#emax=8 can request 1:00 with 16G
#emax=10 can request 6:00 with 50G


##########PARAMETERS TO CHANGE BEFORE RUN###################
emax = [4,6,8]
time = ["00:10:00", "00:15:00", "02:00:00"]
memory = ['1G', "4G", "20G"]
# mass =  [17]
# emax = [10]
# time = ["08:00:00"]
# memory = ["100G"]
# emax = [4]
# time = ["00:10:00"]
# memory = ['1G']
mass =  [22]
Nucleus = "Al"
vs = 'sd-shell'
state = "+1"
# num_samples = 100
###########################################################


def getNucl(Nucl, A):
  return f'{Nucl}{A}'


LECs = ['Ct1S0pp','Ct1S0np','Ct1S0nn','Ct3S1','C1S0','C3P0','C1P1','C3P1','C3S1','CE1','C3P2','c1','c2','c3','c4','cD','cE']
# df = pd.read_csv("/work/submit/abelley/imsrg_toolkit/data/8000Samples.txt")

# index = np.array(df.index)
# rng = np.random.default_rng(seed=42)
# index = rng.choice(index, num_samples, replace=False, shuffle=False)
c2s = [-1.05,-1,-0.95,-0.9, -0.85, -0.8,-0.75,-0.7,-0.65,-0.6,-0.55,-0.5,-0.45,-0.4,-0.3,-0.25, -0.2, -0.15, -0.1, -0.05, 0, 0.05 ]
# c2s = [-0.75,-0.7,-0.65,-0.6,-0.55,-0.5,-0.45,-0.4,-0.3,-0.25]
weights = [-0.33240194, -0.33954467, -0.33478173, -0.23955455,  2.55206001, 0.45721983,
   0.02596174, -1.00661369,  0.76901682,  0.3655842,  -0.83388486, -0.75019334,
  -0.37186834, -0.81926898,  1.04056735,  0.89864506,  0.28259456]


for A in mass:
  for e, t, m in zip(emax,time, memory):
    Nucl = getNucl(Nucleus, A)
    if 3*e < 28:
      E3max = 3*e
    else:
      E3max = 28
    imsrg_params = {}
    imsrg_params['emax'] = e
    imsrg_params['E3max'] = E3max
    imsrg_params['hw'] = 10
    imsrg_params['A'] = A
    imsrg_params['opnames'] = ['Rp2']
    imsrg_params['ref'] = Nucl
    imsrg_params['valence_space'] = vs # this is just a label when custom_valence_space is set
    imsrg_params['label'] = 'SampleDelta'
    imsrg_params['run_cmd'] = """\
  srun apptainer exec \\
    --bind /home/submit \\
    --bind /work/submit \\
    --bind /scratch/submit \\
    --bind /ceph/submit \\
    /work/submit/abelley/pyimsrg.sif """

    kshell_params = {}
    kshell_params['run_cmd'] = """\
  srun apptainer exec \\
    --bind /home/submit \\
    --bind /work/submit \\
    --bind /scratch/submit \\
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

# count = 0
    # for i in index:
    #   sample = df.iloc[i]
    #   SampleID = int(sample["SampleID"])
    #   weights = list(sample[LECs])
    for i,c2 in enumerate(c2s):
      # sample = df.iloc[i]
      SampleID = 1e10+i
      weights[-5] = c2 

      imsrg_params['header'] = f"""#!/bin/bash
#SBATCH --job-name={imsrg_params['ref']}_emax{imsrg_params['emax']}_Sample{SampleID}_%j
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --output=/work/submit/abelley/results/imsrg_log/outputs/{imsrg_params['ref']}_emax{imsrg_params['emax']}_Sample{SampleID}_%j.txt
#SBATCH --error=/work/submit/abelley/results/imsrg_log/errors/{imsrg_params['ref']}_emax{imsrg_params['emax']}_Sample{SampleID}_%j.txt
#SBATCH --time={t}
#SBATCH --mem={m}

cd $SLURM_SUBMIT_DIR
export OMP_NUM_THREADS=24
"""



      header_expvals = f"""#SBATCH --output=/work/submit/abelley/results/kshell_log/outputs/{imsrg_params['ref']}_emax{imsrg_params['emax']}_Sample{SampleID}_eval_%j.txt
#SBATCH --error=/work/submit/abelley/results/kshell_log/errors/{imsrg_params['ref']}_emax{imsrg_params['emax']}_Sample{SampleID}_eval_%j.txt"""

      imsrg_submit = Utils(Nucl, [state, state], imsrg_params, kshell_params, SampleID=SampleID)
      imsrg_submit.submit_all_combine_delta(weights, SampleID, f"{imsrg_submit.output_dir}/{imsrg_submit.filebase}_R2p.csv", header_expvals = header_expvals)
      # count +=1 