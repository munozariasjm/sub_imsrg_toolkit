import sys
# from imsrg_toolkit.imsrg import Imsrg
from imsrg_toolkit.kshell_utils import KshellWavefunctionScript, KshellDensityScript, KshellToolkit
from imsrg_toolkit.utils import Utils
import numpy as np
import pandas as pd



LECs = ['Ct1S0pp','Ct1S0np','Ct1S0nn','Ct3S1','C1S0','C3P0','C1P1','C3P1','C3S1','CE1','C3P2','c1','c2','c3','c4','cD','cE']
df = pd.read_csv("/work/submit/abelley/imsrg_toolkit/data/8000Samples.txt")


# index = np.array([1728])
# sample1 = [0.356199,-0.355142,-0.349985,-0.248157,2.78763,0.433097,-0.086705,-1.299329,0.788,0.520089,-0.846265,-0.736674,-0.606916,-0.47898,0.930314,-0.588286,-0.068944]
# sample13 = [-0.349296,-0.34783,-0.345087,-0.251179,2.775803,0.51126,-0.014905,-0.995633,0.932483,0.358223,-0.787001,-0.707744,-0.441933,-0.706367,0.998484,0.493866,0.372671]
# samples = [sample1, sample13]
# Nucl = "Al22"
# emax = [4,6,8,10]
# time = ["00:10:00","00:30:00", "02:00:00","08:00:00"]
# memory = ['10G', "10G", '20G',"100G"]
emax = [10]
time = ["08:00:00"]
memory = ['100G']
samples_numbers = [100]
# As = [22,23,24,25,26,27]
# states = ['4+1',"2.5+1", "4+1", "2.5+1", "5+1", "2.5+1"]
As = [26,27]
states = ["5+1", "2.5+1"]

for A, state in zip(As,states):
  Nucl = f"Al{A}" 
  imsrg_params = {}
  imsrg_params['E3max'] = 28
  imsrg_params['hw'] = 10
  # imsrg_params['BetaCM'] = 0
  imsrg_params['A'] = A
  imsrg_params['opnames'] = ['Rn2']
  # imsrg_params['opfiles'] = opfiles = [['/work/submit/abelley/operators/M1_2BC_bare_hw10_emax12_e2max24.me2j.gz',"M1_2BC"]]
  imsrg_params['ref'] = Nucl
  imsrg_params['valence_space'] = '0hw-shell' # this is just a label when custom_valence_space is set
  imsrg_params['label'] = 'SampleDelta'
  # imsrg_params['denominator_delta'] = 10
  imsrg_params['run_cmd'] = """\
srun apptainer exec \\
  --bind /home/submit \\
  --bind /work/submit \\
  --bind /scratch/submit \\
  --bind /cvmfs \\
  --bind /ceph/submit \\
  /work/submit/abelley/pyimsrg.sif """
  kshell_params = {}
  kshell_params['run_cmd'] = """\
mpirun -np $SLURM_NTASKS"""
  
  for e, t, mem, num in zip(emax, time, memory, samples_numbers):
    index = np.array(df.index)
    rng = np.random.default_rng()
    index = rng.choice(index, num, replace=False, shuffle=False)
    imsrg_params['emax'] = e
    
  
    for i in index:
      sample = df.iloc[i]
      SampleID = int(sample["SampleID"])
      weights = list(sample[LECs])

  # for i, sample in enumerate(samples):
  #   sample = df.iloc[i]
  #   SampleID = i
  #   weights = sample

      imsrg_params['header'] = f"""#!/bin/bash
#SBATCH --job-name={imsrg_params['ref']}_emax{imsrg_params['emax']}_Sample{SampleID}_%j
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output=/work/submit/abelley/results/imsrg_log/outputs/{imsrg_params['ref']}_emax{imsrg_params['emax']}_Sample{SampleID}_%j.txt
#SBATCH --error=/work/submit/abelley/results/imsrg_log/errors/{imsrg_params['ref']}_emax{imsrg_params['emax']}_Sample{SampleID}_%j.txt
#SBATCH --time={t}
#SBATCH --mem={mem}

cd $SLURM_SUBMIT_DIR
export OMP_NUM_THREADS=24
"""
      kshell_params['header'] = f"""#!/bin/bash
#SBATCH --job-name=kshell_{Nucl}_emax{imsrg_params['emax']}_Sample{SampleID}_%j
#SBATCH --nodes=1
#SBATCH --ntasks=1  
#SBATCH --cpus-per-task=10
#SBATCH --output=/work/submit/abelley/results/kshell_log/outputs/{imsrg_params['ref']}_emax{imsrg_params['emax']}_Sample{SampleID}_%j.txt
#SBATCH --error=/work/submit/abelley/results/kshell_log/errors/{imsrg_params['ref']}_emax{imsrg_params['emax']}_{SampleID}_%j.txt
#SBATCH --time=30:00
# ulimit -s unlimited
module load mpi """





      imsrg_params['SampleID'] =  SampleID
      imsrg_params['LECs'] =  weights
      header_expvals = f"""#SBATCH --output=/work/submit/abelley/results/kshell_log/outputs/{imsrg_params['ref']}_emax{imsrg_params['emax']}_Sample{SampleID}_eval_%j.txt
  #SBATCH --error=/work/submit/abelley/results/kshell_log/errors/{imsrg_params['ref']}_emax{imsrg_params['emax']}_Sample{SampleID}_eval_%j.txt"""

      imsrg_submit = Utils(Nucl, [state,state], imsrg_params, kshell_params)
      imsrg_submit.submit_all_combine_delta(f"{imsrg_submit.output_dir}/{imsrg_submit.filebase}_ops.csv", header_expvals = header_expvals, ops_rankJ = [0], verbose=True)
  # fn_ops = [f"{imsrg_submit.output_dir}{imsrg_submit.filebase}_{op}.snt" for op in imsrg_submit.opnames]
  # tmp = [f"{imsrg_submit.output_dir}{imsrg_submit.filebase}_{op[1]}.snt" for op in imsrg_submit.opfiles]
  # fn_ops.extend(tmp)
  # imsrg_submit.kshell.submit_all(f"{imsrg_submit.output_dir}/{imsrg_submit.filebase}_ops.csv", fn_ops,  ops_rankJ = [0,1,1],  verbose=True, header=header_expvals, gen_partition=True)