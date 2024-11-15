from pyIMSRG import *
from sys import stdout
from pathlib import Path

class imsrg_toolkit():

  def __init__(self):
    #### Here are the default parameters for the imsrg
    self.__default_params()
    

  def __default_params(self):
    ### TODO add all IMSRG parameters in the params
    ### TODO add configuration file to set up the paths
    self.params = {
      #paths
      'scratch': '/scratch/submit/',
      'outputs': '/work/submit/abelley/results/',
      'file2b_path': '/ceph/submit/data/group/ab-initio/me2j/',
      'file3b_path': '/ceph/submit/data/group/ab-initio/me3j/',
      #Modelspace
      'A' : 6,
      'emax': 2,
      'E3max': 28,
      'hw': 10,
      'ref': 'He6',
      'valence_space':'p-shell',
      'custom_valence_space':None,
      #Interaction
      'label' : 'SampleDelta',
      'input2bme': "",
      'file2e1max': 14,
      'file2e2max': 28,
      'file2lmax': 14,
      'input3bme': "",
      'file3e1max': 16,
      'file3e2max': 32,
      'file3e3max': 28,
      'file3_format': 'no2b',
      'file3_precision': 'half',
      #IMSRG
      'method': 'magnus',
      'denominator_partitioning': 'Epstein_Nesbet',
      'eta_criterion': 1e-6,
      'smax': 500,
      'dsmax': 0.5,
      'ds0': 0.5,
      'denominator_delta': 0,
      'domega': 0.2,
      'omega_norm_max': 0.25,
      'ode_tolerance': 1e-6,
      'core_generator': 'atan',
      'valence_space_generator': 'shell-model-atan',
      #Operators
      'opfiles' : [],
      'opnames': [],
      'write_HO_ops': True,
      'write_HF_ops': True,
    }
    

  def update_params(self, **kwargs):
    for key, value in kwargs.items():
      self.params[key] = value


  def set_imsrgsolver(self):
    """
      Intialize the imsrgsolver based on the parameters saved in params.
    """
    self.imsrgsolver.SetMethod(self.params['method'])
    self.imsrgsolver.SetDenominatorPartitioning(self.params['denominator_partitioning'])
    self.imsrgsolver.SetEtaCriterion(self.params['eta_criterion'])
    self.imsrgsolver.SetSmax(self.params['smax'])
    self.imsrgsolver.SetDsmax(self.params['dsmax'])
    self.imsrgsolver.SetDs(self.params['ds0'])
    self.imsrgsolver.SetDenominatorDelta(self.params['denominator_delta'])
    self.imsrgsolver.SetdOmega(self.params['domega'])
    self.imsrgsolver.SetOmegaNormMax(self.params['omega_norm_max'])
    self.imsrgsolver.SetODETolerance(self.params['ode_tolerance'])


  def init_modelspace(self):
    vs = self.params['valence_space']
    if self.params['custom_valence_space']:
      vs = self.params['custom_valence_space']
    self.ms = ModelSpace(self.params['emax'],self.params['ref'], vs)
    self.ms.SetE3max(self.params['E3max'])
    lmax = self.params['emax']
    self.ms.SetLmax(lmax)
    self.ms.SetHbarOmega(self.params['hw'])
    self.ms.SetTargetMass(self.params['A'])


  def read_interaction(self, file2b, file3b):
    Hbare = Operator(self.ms,0,0,0,3)
    Hbare.SetHermitian()
    if self.params['file3_format'] == 'no2b':
      Hbare.ThreeBody.SetMode('no2b')
    if self.params['file3_precision'] == 'half':
      Hbare.ThreeBody.SetMode("no2bhalf")
    self.rw.ReadBareTBME_Darmstadt(self.params['file2b_path']+file2b, Hbare, 
                                self.params['file2e1max'], 
                                self.params['file2e2max'], 
                                self.params['file2lmax'])
    Hbare.ThreeBody.ReadFile([self.params['file3b_path']+file3b], 
                                  [self.params['file3e1max'], 
                                  self.params['file3e2max'], 
                                  self.params['file3e3max']
                                  ]
                                  )
    Hbare += Trel_Op(self.ms)
    return Hbare
  
  def read_interaction_combine_delta(self, file2b, file3b):
    Hbare = Operator(self.ms,0,0,0,3)
    Hbare.SetHermitian()
    if self.params['file3_format'] == 'no2b':
      Hbare.ThreeBody.SetMode('no2b')
    if self.params['file3_precision'] == 'half':
      Hbare.ThreeBody.SetMode("no2bhalf")
    self.rw.ReadBareTBME_Darmstadt(self.params['file2b_path']+file2b, Hbare, 
                                self.params['file2e1max'], 
                                self.params['file2e2max'], 
                                self.params['file2lmax'])
    Hbare.ThreeBody.ReadFile([self.params['file3b_path']+file3b], 
                                  [self.params['file3e1max'], 
                                  self.params['file3e2max'], 
                                  self.params['file3e3max']
                                  ]
                                  )
    Hbare += Trel_Op(self.ms)
    return Hbare


  def print_estimatePT(self, HNO):
    #Give estimate with perturbation theory to make sure everything is ok
    print("Perturbative estimates of gs energy:")
    EMP2 = HNO.GetMP2_Energy()
    EMP2_3B = HNO.GetMP2_3BEnergy()
    print(f"EMP2 = {EMP2}")
    print(f"EMP2_3B =  {EMP2_3B}")
    Emp_3 = HNO.GetMP3_Energy()
    EMP3 = Emp_3[0]+Emp_3[1]+Emp_3[2]
    print(f"E3_pp = {Emp_3[0]}  E3_hh = {Emp_3[1]}  E3_ph = {Emp_3[2]} EMP3 =  {EMP3}")
    print(f"To 3rd order, E = {HNO.ZeroBody + EMP2 + EMP3 + EMP2_3B}")
    stdout.flush()  #So that print statement are in the right order


  def write_op_to_file(self, op, opname, extra=None):
    filename = f"{self.intfile}_{opname}"
    if extra:
      filename += f"_{extra}"
    filename += ".snt"
    if (op.GetJRank() == 0 and op.GetTRank() == 0 and op.GetParity() == 0):
      self.rw.WriteTokyo(op, filename, "op")
    else:
      self.rw.WriteTensorTokyo(filename,op)


  def evolve_operators(self):
    if len(self.params['opnames']) != 0:
      for i,opname in enumerate(self.params['opnames']):
          print(f"Starting to evolve {opname}:")
          op = OperatorFromString(self.ms, opname)
          if self.params['write_HO_ops']:
            print(f"Writing HO operators to {self.output_dir}")
            self.write_op_to_file(op, opname, extra = "HO")
          op = self.hf.TransformToHFBasis(op)
          if self.params['write_HF_ops']:
            op = op.DoNormalOrderingCore()
            print(f"Writing HF operators to {self.output_dir}")
            self.write_op_to_file(op, opname, extra = "HF")
            op = op.UndoNormalOrdering()
          op = op.DoNormalOrdering()
          op = self.imsrgsolver.Transform(op)
          op = op.UndoNormalOrdering()
          op = op.DoNormalOrderingCore()
          print( opname , 'zero body = ', op.ZeroBody)
          self.write_op_to_file(op, opname)
    if len(self.params['opfiles']) != 0:
      print("Opeator from file not yet implemented.")
      print("Continuing...")


  def run(self, file2b, file3b):
    #Initiate the ReadWrite class to access files
    self.rw = ReadWrite()

    #Create the model space for the nuclei
    self.init_modelspace()

    #Create the input hamiltonian from the 2b and 3b file
    Hbare = self.read_interaction(file2b, file3b)

    #Solve HFMBPT to obtain reference state
    self.hf = HFMBPT( Hbare )
    self.hf.Solve()
    HNO = self.hf.GetNormalOrderedH(2)

    #Give estimate with perturbation theory to make sure everything is ok
    self.print_estimatePT(HNO)
    
    #Initialize the IMSRGSolver instance and set parameters
    self.imsrgsolver = IMSRGSolver(HNO)
    self.imsrgsolver.SetHin(HNO)
    self.imsrgsolver.SetReadWrite(self.rw)
    #Set parameters for the IMSRG solver
    self.set_imsrgsolver()

    #Decouple the core
    self.imsrgsolver.SetGenerator(self.params['core_generator'])
    self.imsrgsolver.Solve()

    #Update IMSRG params for the decoupling of the valence-space
    self.imsrgsolver.SetSmax( 2*self.params['smax'])
    self.imsrgsolver.SetGenerator(self.params['valence_space_generator'])
    self.imsrgsolver.Solve()

    #### Get evolved Hamiltonian NO wrt the core
    HNO = self.imsrgsolver.GetH_s()
    HNO = HNO.UndoNormalOrdering()
    HNO = HNO.DoNormalOrderingCore()

    # Write things to disk
    self.output_dir = f"{self.params['outputs']}/{self.params['ref']}/{self.params['label']}/"
    Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    print(f'Writing output file to {self.output_dir}')
    self.gen_filebase()
    self.intfile = f"{self.output_dir}/{self.filebase}"
    self.rw.WriteTokyo(HNO,self.intfile+".snt", "")
    stdout.flush()
    
    # Evolve operators 
    self.evolve_operators()
       
    # # #Write_kshell_jobs to be submitted after the imsrg has ran
    # for states in params["state_lists"]:
    #   kshl_r, f_diag_r = write_kshell_diag(params['path_to_kshell'], intfile+".snt", params['Nucl'], params['hw_truncation'], params['ph_truncation'], params['header'], gen_partition=True, states=states[0])
    #   if params['Nucl_daughter']:
    #     kshl_l, f_diag_l = write_kshell_diag(params['path_to_kshell'], intfile+".snt", params['Nucl_daughter'], params['hw_truncation'], params['ph_truncation'], params['header'], gen_partition=True, states=states[1])
  

  def gen_filebase(self):
    self.filebase = f"{self.params['valence_space']}_{self.params['ref']}_{self.params['method']}_e{self.params['emax']}_E{self.params['E3max']}_hw{self.params['hw']}"






class kshell_tookit():

  def __init__(self):
    pass

  def __default_params(self):
    self.params = {
      #Kshell
      'Nucl_daughter': None,
      'path_to_kshell': " ",
      'Nucl': "He6",
      'header': " ",
      'state_lists': [("+1","+1")],
      'hw_truncation': None,
      'ph_truncation': None,
      }
    


