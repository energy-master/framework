# %% [markdown]
# ## Harbour Popoise Detection Algorithm
# 

# %% [markdown]
# Ownership & Copyright Rahul Tandon, RSAqua 2024

# %%
## 
# ===================================================
# | Harbour Popoise Detection Genetic Algorithm     |
# ===================================================
#
#
#  c. Rahul Tandon, 2024, RSA 2024 
##

# %% [markdown]
# ### Imports

# %%

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
import inspect

from rich import pretty
from rich.console import Console
pretty.install()
from rich import print as rprint
from rich.progress import Progress


load_dotenv()
config = dotenv_values("marlin_hp.env")
logging.basicConfig(level=logging.CRITICAL)


# --- FILE PATHS

# add application root to path
app_path = config['APP_DIR']
sys.path.insert(0, app_path)

# add brahma to system path
brahma_path = config['BRAHMA_DIR']
sys.path.insert(0, brahma_path)


# Define location of bespoke genes
GENETIC_DATA_FOLDER_USR = os.path.join(os.path.expanduser(
    '~'), 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_genes', '')
os.environ['GENETIC_DATA_FOLDER_USR'] = GENETIC_DATA_FOLDER_USR
sys.path.insert(0, os.environ['GENETIC_DATA_FOLDER_USR'])


# Define location of bespoke bots
BOT_DATA_FOLDER_USR = os.path.join(os.path.expanduser(
    '~'), 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_bots', '')
os.environ['CUSTOM_BOT_FOLDER_USR'] = BOT_DATA_FOLDER_USR
sys.path.insert(0, os.environ['CUSTOM_BOT_FOLDER_USR'])

# Define bespoke decision logic
DECISION_FOLDER_USR = os.path.join(os.path.expanduser(
    '~'), 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_decisions', '')
os.environ['DECISION_FOLDER_USR'] = DECISION_FOLDER_USR
sys.path.insert(0, os.environ['DECISION_FOLDER_USR'])

# import evolutionary procedures
import marlin_brahma.bots.bot_root as bots
import marlin_brahma.world.population as pop
from marlin_brahma.fitness.performance import RootDecision
import marlin_brahma.fitness.performance as performance



#import app 
# from marlin_hp.custom_bots.mybots import *
from custom_bots import *
from custom_genes import *
from custom_decisions import *





# from marlin_brahma.world.population import *

# # Define location of bespoke genes
# GENETIC_DATA_FOLDER_USR = os.path.join(os.path.expanduser(
#     '~'), 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_genes', '')
# os.environ['GENETIC_DATA_FOLDER_USR'] = GENETIC_DATA_FOLDER_USR
# sys.path.insert(0, os.environ['GENETIC_DATA_FOLDER_USR'])


# # Define location of bespoke bots
# BOT_DATA_FOLDER_USR = os.path.join(os.path.expanduser(
#     '~'), 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_bots', '')
# os.environ['CUSTOM_BOT_FOLDER_USR'] = BOT_DATA_FOLDER_USR
# sys.path.insert(0, os.environ['CUSTOM_BOT_FOLDER_USR'])

# # Define bespoke decision logic
# DECISION_FOLDER_USR = os.path.join(os.path.expanduser(
#     '~'), 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_decisions', '')
# os.environ['DECISION_FOLDER_USR'] = DECISION_FOLDER_USR
# sys.path.insert(0, os.environ['DECISION_FOLDER_USR'])



# %% [markdown]
# ### Class definitions

# %% [markdown]
# #### Setup Class

# %%

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
            
   

# %% [markdown]
# #### Main Application Class

# %%
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
        
        # performance and evaluation
        self.performance = None
    
    
    def generation_reset(self):
        self.performance = performance.Performance()
    
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
    
        rprint (f"Data Download complete.")
        rprint (f"Number of simulation snapshots downloaded: {data_adapter.number_sim_snapshots}")
        rprint (f"Number of marlin data acquisition runs: {data_adapter.number_runs}")
        
        rprint ("Building Datafeed")
    
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
      

# %% [markdown]
# #### Bot Interation Routine

# %%
def bot_iteration(bot : bots = None, data_adapter : MarlinData = None, data_feed : MarlinDataStreamer = None, config : dict[str : str] = None) -> int:
    if bot is not None:
        
        # reset data feed for new iteration
        #data_feed.reset()
        listen_start_idx = 0
        listen_end_idx = 0
        for env_pressure in data_feed:
            
            listen_delta_idx = config['listen_delta_t'] * env_pressure.meta_data['sample_rate']
            env_pressure_length = env_pressure.frequency_ts_np.shape[0]
            sample_rate = env_pressure.meta_data['sample_rate']
            
            while listen_start_idx < env_pressure_length:
                
                # --- get start & end slice idx ---
                listen_end_idx = listen_start_idx + listen_delta_idx
                slice_start = listen_start_idx
                slice_end = min(listen_end_idx,env_pressure_length-1)
                
                # --- get datetime ---
                _s = (slice_start / env_pressure.meta_data['sample_rate']) * 1000 # ms 
                iter_start_time =  env_pressure.start_time +    timedelta(milliseconds=_s)
                _s = (slice_end / env_pressure.meta_data['sample_rate']) * 1000
                iter_end_time   =  env_pressure.start_time  +   timedelta(milliseconds=_s)
                # print (f'{iter_start_time} : {iter_end_time}')
                
                # --- express bot ---
                # [nb. data structure is passed to individual genes if dna is initialised.
                # extra data can be added under 'init_data' field]
                express_value = bot.ExpressDNA(data = {'current_data' :  env_pressure.frequency_ts_np.shape[slice_start:slice_end], 'derived_model_data' : data_adapter.derived_data, 'iter_start_time' : iter_start_time, 'iter_end_time' : iter_end_time})
                # print (f'Express level: {bot.dNAExpression}')
                
                # --- transcription ---
                # print (bot.transcriptionDNA.transcription_threshold)
                transcription_data = {
                    'expression_data': bot.GetExpressionData(),
                }
                
                transcribe_result = bot.transcriptionDNA.transcribe(transcription_data)
                # print (transcribe_result)
                
                
                # ======Decision & Marking=========================
                # --- make and add decision ---
                
                decision_args = {
                    'status' : 1,
                    'env' : config['env'],
                    'iter_start_time' : iter_start_time,
                    'iter_end_time' : iter_end_time,
                    'action' : 1,
                    'type' : "HP Ident"
                    
                }
                
                new_decision = IdentDecision(decision_data=decision_args)
                application.performance.add_decision(decision=new_decision, epoch = "1", botID = bot.name)
                
                
                # ================================================
                # query dataset to mark decision
                # ================================================
                xr = False
                xr_data = data_adapter.derived_data.query_label(iter_start_time, iter_end_time)
                if xr_data['xr']:
                    print ("match")
                    print (xr_data)
                    xr = True
                
               
                
                # ================================================
               
                
                
                decision_args = {
                    'status' : 0,
                    'env' : config['env'],
                    'iter_start_time' : iter_start_time,
                    'iter_end_time' : iter_end_time,
                    'action' : 0,
                    'type' : "HP Ident",
                    'success' : xr
                }
                close_decision = IdentDecision(decision_data=decision_args)
                application.performance.add_decision(decision=close_decision, epoch = "1", botID = bot.name)
                
                
                
                # =================================================
                
                
                # update listen start idx
                listen_start_idx = listen_end_idx
                
            
    else:
        logging.debug("Bot not alive!")

# %% [markdown]
# #### Entry, Data Initialisation, and World Creation 

# %%
     
# --------------------------------------------------------------
# --- Entry Function ---                                       |
# --------------------------------------------------------------


# if __name__ == "__main__":
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)
rprint(f'logging level : {logger.level}')
# --- ALGORITHM SETUP ---


rprint ("Creating algorithm setup")
algo_setup = AlgorithmSetup(config_file_path="config.json")

rprint ("Creating Application")
application = SpeciesIdent(algo_setup)

rprint ("Creating world")
application.build_world()

# --- DATA CONNECTION AND DOWNLOAD ---


# Grab data snapshot ids from Marlin Ident
data_src_json = "data_conn_neltey.json"
with open(data_src_json) as fp:
    src_data_snapshots = json.load(fp)
    

# --------------------------------------------------------------
# --- 1. Download data from RSA signature and simualtion db -  |
# --------------------------------------------------------------
# rprint ("Building Adapter")
# # create the data adapter
# data_adapter = MarlinData(load_args={'limit' : 100000})

# # download signature data
# rprint(f"[Downlaod Signature Snapshots]")
# #data_adapter.download_signatures(load_args = {'signature_ids' : []})

# # print (src_data_snapshots)
# # download simulation snapshots
# rprint(f"[Downlaod Simulation Snapshots]")
# src_data_snapshots = list(map(int, src_data_snapshots))
# # data_adapter.download_simulation_snapshots(load_args = {'location' : 'netley', 'ss_ids' : src_data_snapshots})
# data_adapter.download_simulation_snapshots(load_args = {'location' : algo_setup.args['data_location']})
# rprint (f"Data Download complete.")

simulation_data_path = "/home/vixen/rs/data/acoustic/ellen/raw_repo/hp/sim"
signature_data_path = "/home/vixen/rs/data/acoustic/ellen/raw_repo/hp/sig"

data_adapter = MarlinData(load_args={'limit' : 100000})
data_adapter.load_from_path(load_args={'load_path' :simulation_data_path, "snapshot_type":"simulation"})
data_adapter.load_from_path(load_args={'load_path' :signature_data_path, "snapshot_type":"signature"})




# ---------------------------------------------------------------
# --- 2. Build datafeed                                         |
# ---------------------------------------------------------------
rprint ("Building Simulation Datafeed")

# create a MarlinDataStreamer
data_feed = MarlinDataStreamer()

# initilise the simulation datafeeder with downloaded data in data_adapter
data_feed.init_data(data_adapter.simulation_data, data_adapter.simulation_index)

# randomise setup parameters
batch_id = random.randint(0,99999)
sample_number = 0

# build labelled data streamer
labelled_data_feed = MarlinDataStreamer()
labelled_data_feed.init_data(data_adapter.signature_data, data_adapter.signature_index)

# ---------------------------------------------------------------
# --- 3. Build derived data                                    |
# ---------------------------------------------------------------
rprint ("Building Derived Data")

# buid derive data structure
data_adapter.build_derived_data(n_fft=2048)

for data_inst in data_feed:
    snap_id = data_inst.meta_data['snapshot_id']
    print (f'building: {snap_id}')
    data_adapter.derived_data.build_derived_data(data_inst)
    # print (f'{data_inst.start_time}')

for labelled_data in labelled_data_feed:
    data_adapter.derived_data.build_derived_labelled_data(signature_data=labelled_data)


print ("\n")
print (f'Data start time : {data_adapter.derived_data.data_start_time} End time : {data_adapter.derived_data.data_end_time}')
print (f'Number of energy frames : {data_adapter.derived_data.number_energy_frames}')
print (f'Maximum f : {data_adapter.derived_data.max_freq}')
print (f'Minimum f : {data_adapter.derived_data.min_freq}')
print (f'Delta f : {data_adapter.derived_data.delta_frequency}')



# %% [markdown]
# ### Optimisation

# %% [markdown]
# Having built the world and connected it to the data, we can now optimise the bots.

# %%

# download labelled data
#data_adapter.download_signature_snapshots(load_args={"limit":100000})

# # build labelled data streamer
# labelled_data_feed = MarlinDataStreamer()
# labelled_data_feed.init_data(data_adapter.signature_data, data_adapter.signature_index)

# build lablled data structure in derived data required for cross referencing (xr)
# for labelled_data in labelled_data_feed:
#     data_adapter.derived_data.build_derived_labelled_data(signature_data=labelled_data)


# ---------------------------------------------------------------
# --- 3. Run World      ---                                     |
# ---------------------------------------------------------------


for generation_number in range(0, algo_setup.args['number_generations']):

    # build generational performance management
    application.generation_reset()
   
    for individual_idx in range(0, algo_setup.args['population_size']):
        
        # get bot name
        bot_name = application.population.bots[individual_idx]
        
        # debug -> bot data
        _bot = application.population.species[bot_name]
        #print (_bot.printStr())
        
        # run bot iteration
        #iter_res = bot_iteration(application.population.species[bot_name], data_adapter, data_feed, config=algo_setup.args)
        
    # show decisions
    # application.performance.showBotDecisions()
    
    # evaluate & rank
    application.performance.evaluateBots(application.population.species, args=algo_setup.args)
    application.performance.text_output_fitness()
    # evolution
    
    
        
        
    
    
    


