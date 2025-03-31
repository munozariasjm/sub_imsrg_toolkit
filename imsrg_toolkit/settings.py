import os
#Get the unsername of the the user on the cluster
username = os.environ['USER']
#Finds the absolute path where imsrg_toolkit is installed
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
