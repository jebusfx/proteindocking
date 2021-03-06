from sys import stdout
from os import path    
from datetime import datetime
from time import sleep
from alpsdocking import ALPSDocking
from alps.alps import ALPS, ALPSException
from bio.dockingproblem import DockingProblem
from alps.definitions.crossover import single_point
from alps.definitions.agingscheme import fibonacci
from alps.definitions.selection import enhanced
from alps.definitions.stopcondition import gen_limit  
from pymol import cmd
from Queue import Queue
from threading import Thread
from traceback import format_exception
from sys import exc_info

class ALPSMain(Thread):
    def __init__(self,queue,protein_path,ligand_path,itp_path,cavities_path,output_path,forcefield,files_path):
        super(ALPSMain, self).__init__()
        self.queue = queue
        self.protein_path = str(protein_path)
        self.ligand_path = str(ligand_path)
        self.itp_path = str(itp_path)
        self.cavities_path = str(cavities_path)
        self.output_path = output_path
        self.forcefield = forcefield        
        self.FILES_PATH = files_path
        self.ex_queue = Queue()

    def display_dockedpair(self,docking):
        LIGAND = 'ligand'
        PROTEIN = 'protein'
        CAVITIES = 'cavities'
        cmd.load(docking.pair_file)
        cmd.hide('all')
        cmd.select(LIGAND,'resn {}'.format(docking.ligand_id[:3]))
        cmd.select(PROTEIN,'chain *')
        cmd.select(CAVITIES,'resn Cl*') 
        cmd.show('sticks',LIGAND)
        cmd.show('ribbon',PROTEIN)
        cmd.show('spheres',CAVITIES)    
        cmd.delete(LIGAND)
        cmd.delete(PROTEIN)
        cmd.delete(CAVITIES)

    def run(self):                
        try:                        
            docking = ALPSDocking(self.ligand_path, self.protein_path, self.cavities_path, self.itp_path, self.FILES_PATH, self.forcefield)        
            docking._run_pymol(self.output_path,self.queue)
            self.queue.put("Docking complete.\nPDB file: {0}".format(docking.pair_file))
            self.display_dockedpair(docking)
        except ALPSException as ae:      
            self.ex_queue.put(ae)
        except Exception as e:
            exc_type, exc_value, exc_traceback = exc_info()            
            self.ex_queue.put(repr(format_exception(exc_type, exc_value,exc_traceback)) + repr(e))              