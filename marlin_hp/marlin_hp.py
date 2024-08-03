#!/usr/bin/python3


"""

    RSA Aqua.
    c. Rahul Tandon 2024
    =================================================
    Harbour porpoise detection algorithm. 

"""

# import marlin data adapter
from marlin_data.marlin_data import *
# import marlin building blocks
from marlinblocks import acoustic_frame as af
from marlinblocks import model_frame as mf
from marlinblocks import snapshot as snaps 
from marlinblocks import geo_frame as gf
# datetime import
from datetime import datetime, timedelta
# numpy import
import numpy as np
# import logging, os and sys
import logging, os, sys
# import dotenv
from dotenv import load_dotenv, dotenv_values


from rich import pretty
from rich.console import Console
pretty.install()
from rich import print as rprint
from rich.progress import Progress


load_dotenv()
config = dotenv_values("marlin_hp.env")
logging.basicConfig(level=logging.CRITICAL)


# add application root to pathß
app_path = config['APP_DIR']
sys.path.insert(0, app_path)

# add brahma to system path
brahma_path = config['BRAHMA_DIR']
sys.path.insert(0, brahma_path)


#import app 
# from marlin_hp.custom_bots.mybots import *
from custom_bots import *
from custom_genes import *

# import evolutionary procedures
import marlin_brahma.bots.bot_root as bots
import marlin_brahma.world.population as pop
# from marlin_brahma.world.population import *

#define location of bespoke genes
GENETIC_DATA_FOLDER_USR = os.path.join(os.path.expanduser(
    '~'), 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_genes', '')
os.environ['GENETIC_DATA_FOLDER_USR'] = GENETIC_DATA_FOLDER_USR
sys.path.insert(0, os.environ['GENETIC_DATA_FOLDER_USR'])


# define location of bespoke bots
BOT_DATA_FOLDER_USR = os.path.join(os.path.expanduser(
    '~'), 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_bots', '')
os.environ['CUSTOM_BOT_FOLDER_USR'] = BOT_DATA_FOLDER_USR
sys.path.insert(0, os.environ['CUSTOM_BOT_FOLDER_USR'])



# --------------------------------------------------------------
# --- Setup Class ---                                          |
# --------------------------------------------------------------

class AlgorithmSetup(object):
    """Class to control optimisation algorithm.

    Args:
        object (): root class object
    """     
    def __init__(self, config_file_path : str = "config.json"):
        
        self.args = {}
        
        #load config file
        run_config = None
        with open(config_file_path, 'r') as config_f:
            run_config = json.load(config_f)
            
        if run_config is not None:
           self.args = run_config
            
            

# --------------------------------------------------------------
# --- Main Application Class ---                               |
# --------------------------------------------------------------

class SpeciesIdent(object):
    """_summary_

    Args:
        object (_type_): _description_
    """    
    def __init__(self, setup : AlgorithmSetup = None):
        self.algo_setup = setup
        self.batch_id = random.randint(0,99999)
        self.population = None
        
    def connect_and_stream(self, download_args : {} = None) -> MarlinDataStreamer:
        """_summary_
        
        Args:
            download_args (None, optional): _description_. Defaults to None.

        Returns:
            MarlinDataStreamer: _description_
        """     
        # create the data adapter
        data_adapter = MarlinData(load_args=download_args)
        
        # download signature data
        #rprint(f"[Downlaod Signature Snapshots]")
        #data_adapter.download_signatures(load_args = {'signature_ids' : []})
    
        # download simulation snapshots
        rprint(f"[Downlaod Simulation Snapshots]")
        data_adapter.download_simulation_snapshots(load_args = download_args)
    
        print (f"Data Download complete.")
        print (f"Number of simulation snapshots downloaded: {data_adapter.number_sim_snapshots}")
        print (f"Number of marlin data acquisition runs: {data_adapter.number_runs}")
        
        print ("Building Datafeed")
    
        # create a MarlinDataStreamer
        data_feed = MarlinDataStreamer()
        # initilise the simulation datafeeder with downloaded data in data_adapter
        data_feed.init_data(data_adapter.simulation_data, data_adapter.simulation_index)
        
        return data_feed
        
    def run(self):
        pass
    
    def build_world(self):
        """Build the population of bots using brahma_marlin. Genes are present in ../genes
        """
        
        try:
            logging.debug('Building population')
            self.population = pop.Population(parms=self.algo_setup.args, name="hp_classifier")
            self.population.Populate(species="AcousticBot", args = None)
            logging.debug("Population built")
        except Exception as err:
            logging.critical(f"Error building population {err=} {type(err)=}")
        
    def evolve_world(self):
        pass
    
    def output_world(self):
        pass
        
        
# --------------------------------------------------------------
# --- Entry Function ---                                       |
# --------------------------------------------------------------


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    logger = logging.getLogger(__name__)
    print(f'logging level : {logger.level}')
    # --- ALGORITHM SETUP ---
    
    
    print ("Creating algorithm setup")
    algo_setup = AlgorithmSetup(config_file_path="config.json")
    
    print ("Creating Application")
    application = SpeciesIdent(algo_setup)
    
    print ("Creating world")
    application.build_world()
    
    # --- DATA CONNECTION AND DOWNLOAD ---
    
    
    # Grab data snapshot ids from Marlin Ident
    data_src_json = "data_conn_neltey.json"
    with open(data_src_json) as fp:
        src_data_snapshots = json.load(fp)
        
    
    # --------------------------------------------------------------
    # --- 1. Download data from RSA signature and simualtion db -  |
    # --------------------------------------------------------------
    print ("Building Adapter")
    # create the data adapter
    data_adapter = MarlinData(load_args={'limit' : 10})
    
    # download signature data
    print(f"[Downlaod Signature Snapshots]")
    #data_adapter.download_signatures(load_args = {'signature_ids' : []})
    
    # print (src_data_snapshots)
    # download simulation snapshots
    print(f"[Downlaod Simulation Snapshots]")
    src_data_snapshots = list(map(int, src_data_snapshots))
    
   
    data_adapter.download_simulation_snapshots(load_args = {'location' : 'netley', 'ss_ids' : src_data_snapshots})

    
    print (f"Data Download complete.")
   
    
    # ---------------------------------------------------------------
    # --- 2. Build datafeed ---                                     |
    # ---------------------------------------------------------------
    print ("Building Datafeed")
    
    # create a MarlinDataStreamer
    data_feed = MarlinDataStreamer()
    # initilise the simulation datafeeder with downloaded data in data_adapter
    data_feed.init_data(data_adapter.simulation_data, data_adapter.simulation_index)
    
    batch_id = random.randint(0,99999)
    sample_number = 0
    
    for data_inst in data_feed:
        pass

