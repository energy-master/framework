## ---------------------------------------------------------------------------  #
# ===================================================                           #
# | Harbour Popoise Detection Genetic Algorithm     |                           #
# | Bot run                                         |                           #
# ===================================================                           #
#                                                                               #
#                                                                               #
#                                                                               #
#  c. Rahul Tandon, 2024, RSA 2024                                              #
#  GA Game to be presented in all teams July meeting.                           #
## ---------------------------------------------------------------------------- #
import sys
print (sys.argv[0])
command = False
bulk = False
print (sys.argv[4])
if (len(sys.argv) > 1):
    command = True
    my_activation_level = 0.7
    user = sys.argv[1]
    snapshot_id =  sys.argv[2]
    bot_id = sys.argv[3]
    location_str = sys.argv[4]
    filter_data = "*"
    if bot_id == "bulk": 
        filter_data = sys.argv[5]
        bulk = True
        
    else:
        my_activation_level = sys.argv[5]
    

# --------------------------------------------------------------
# --- Imports ---                                          |
# --------------------------------------------------------------
from optimisation_manager import *
# sys, os imports
import sys,os, pickle
import requests, json
# marlin data import -- CUSTOM --
# sys.path.append('../../marlin_data/marlin_data')
sys.path.append('/home/vixen/rs/dev/marlin_data/marlin_data')
from marlin_data import *

# datetime import
from datetime import datetime, timedelta

# dotenv and pretty text
from dotenv import load_dotenv, dotenv_values
import pickle
import inspect
from rich import pretty
from rich.console import Console
pretty.install()
from rich import print as rprint
from rich.progress import Progress

load_dotenv()
config = dotenv_values("/home/vixen/rs/dev/marlin_hp/marlin_hp/marlin_hp.env")
logging.basicConfig(level=logging.INFO)
print (config)

# file paths and BRAHMA -- CUSTOM --\

# add application root to path
app_path = config['APP_DIR']
sys.path.insert(0, app_path)

# add brahma to system path
brahma_path = config['BRAHMA_DIR']
sys.path.insert(0, brahma_path)

# Define location of bespoke genes
GENETIC_DATA_FOLDER_USR = os.path.join('/','home','vixen', 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_genes', '')
os.environ['GENETIC_DATA_FOLDER_USR'] = GENETIC_DATA_FOLDER_USR
sys.path.insert(0, os.environ['GENETIC_DATA_FOLDER_USR'])

# Define location of bespoke bots
BOT_DATA_FOLDER_USR = os.path.join('/','home','vixen', 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_bots', '')
os.environ['CUSTOM_BOT_FOLDER_USR'] = BOT_DATA_FOLDER_USR
sys.path.insert(0, os.environ['CUSTOM_BOT_FOLDER_USR'])

# Define bespoke decision logic
DECISION_FOLDER_USR = os.path.join('/','home','vixen', 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_decisions', '')
os.environ['DECISION_FOLDER_USR'] = DECISION_FOLDER_USR
sys.path.insert(0, os.environ['DECISION_FOLDER_USR'])

NUMBA_CACHE_DIR = os.path.join('/','home','vixen', 'rs','dev', 'marlin_hp', 'marlin_hp', 'cache')
os.environ['NUMBA_CACHE_DIR'] = NUMBA_CACHE_DIR
# IMPORT BRAHMA 
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

# define data load path !- Don't add trailing "/" AND different path for sim and sig
simulation_data_path = "/home/vixen/rs/dev/marlin_hp/marlin_hp/data/sim"
signature_data_path = "/home/vixen/rs/dev/marlin_hp/marlin_hp/data/sig"


#import game code... always after main import headers ( especially sys path updates )
from game import *

#snapshot ids
# sim_ids = ["515890908851898947403331","431429798878348481296633","18384048342489753394866","612410776163767706197959","152113855399211401961333","249872969138326627090783","68793058397733916400301"]
sim_ids = ["82000738700746005197334"]


# ----- Grab snapshot id from command line
limit = len(sim_ids)
limit = 5
if command == True:
    sim_ids = []
    sim_ids.append(snapshot_id)
    print (sim_ids)
    
def load_bot(bot_path):
    print ("loading...")
    print (bot_path)
    file_ptr = open(bot_path, 'rb')
    bot = pickle.load(file_ptr)
    print(bot)
    return bot

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
        id =  random.randint(0,99999)
        self.batch_id = f'brahma_{id}'
        self.population = None
        self.data_feed = None
        self.derived_data = None
        # performance and evaluation
        self.performance = None
        self.algo_setup.args['run_id'] = self.batch_id
        self.loaded_bots = {}
        self.mode = 0
        self.bulk = 0
        self.ss_ids = []
    
    def generation_reset(self):
        self.performance = performance.Performance()
    
    def load_bots(self, filter_data):
        url = 'https://vixen.hopto.org/rs/api/v1/data/features'
        post_data = {'market': filter_data}

        x = requests.post(url, json = post_data)
        data  = x.json()
        number_loaded = 0
        for key in data["data"]:
            
            bot_id = key['botID']
            bot_dir = "/home/vixen/rs/dev/marlin_hp/marlin_hp/bots"
            bot_path = f'{bot_dir}/{bot_id}.vixen'
            # print (bot_path)
            error = False
            
            try:
                bot = load_bot(bot_path)
                print (bot)
                self.loaded_bots[bot_id] = bot
            except:
                error = True
                print (f'error loading {bot_id}')
                
            if  error == False:
                number_loaded+=1
                print (f'success loading {bot_id}')
            
        
        self.mode = 1
        self.bulk = 1
        print (f'number loaded : {number_loaded}')
        
    
    def run(self):
        pass
    
    def build_world(self):
        """Build the population of bots using brahma_marlin. Genes are present in ../genes
        """
        
        try:
            logging.critical('Building population')
            self.population = pop.Population(parms=self.algo_setup.args, name="hp_classifier")
            logging.critical('Building... ')
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

rprint ("Building World")
# if __name__ == "__main__":
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)
rprint(f'Logging Level : {logger.level}')

rprint ("Creating algorithm setup")
algo_setup = AlgorithmSetup(config_file_path="/home/vixen/rs/dev/marlin_hp/marlin_hp/config.json")

# update user if command line
if (command):
    algo_setup.args['user'] = user
    algo_setup.args['active_bot'] = bot_id
    algo_setup.args['snapshot_id'] = snapshot_id
    

rprint ("Creating Application")
application = SpeciesIdent(algo_setup)
application.ss_ids = sim_ids

if (bulk):
    application.load_bots(filter_data)


rprint ("Creating world")
application.build_world()
rprint ("World Created")


# --------------------------------------------------------------
# --- Optimisation Data Manager ---                                          |
# --------------------------------------------------------------
# print (application.algo_setup.args)
optimisationDataManager = OptimisationDataManager(application.algo_setup.args['user'], config=application.algo_setup.args,market = application.algo_setup.args['env'], scope=application.algo_setup.args['scope'], user_uid = application.algo_setup.args['user_uid'], optimisation_id=application.algo_setup.args['run_id'])
# print (optimisationDataManager)
optimisationDataManager.defineDescription()
envList = ['live']
optimisationDataManager.setEnv(envList)
optimisationDataManager.dbSendNewOptimisation()

# --------------------------------------------------------------
# --- Data Acq ---                                       |
# --------------------------------------------------------------

# location / snaphsots must be an array or list of locations or ids
location = ['67149847']
if command:
    location = []
    location.append(location_str)
# --snapshot_ids = []

# Init data adapter (marlin adapter)
data_adapter = None
data_adapter = MarlinData(load_args={'limit' : limit})



    

# data download routine
def download_data():

    # Download data and store locally
    #   -params-
    #   simulation_path : path to save serial data to locally
    #   limit : max number of downlaods
    #   location : location of hydrophone (must be an array)
    #   ss_ids : ids of snapshots
    
    print ("search ids")
    print (sim_ids)
    print ("downloading simulation data")
    data_adapter.download_simulation_snapshots(load_args={ 'location':location, 'ss_ids' : sim_ids})
    # print ("downloading signatures")
    # logging.critical('Downloading data')
    # if command == False:
    #     data_adapter.download_signature_snapshots(load_args={'signature_path':signature_data_path,"limit":10})




# data load routine    
def load_data():
    # Load data into the marlin data adapter from a local source
    #   -params-
    #   load_path : path to local rep of serial data
    #   limit : max number of downlaods
    #   snapshot_type : type of snapshot [ simulation | signature ]
   
    global data_adapter
    logging.critical('Loading data')
    #r = data_adapter.load_from_path(load_args={'load_path' : signature_data_path, "snapshot_type":"signature", "limit" : limit})
    r = data_adapter.load_from_path(load_args={'load_path' : simulation_data_path, "snapshot_type":"simulation", "limit" : limit,  'ss_ids' : sim_ids})
    
data_feed_ = None
data_feed_label = None

def build_feed():
    # Having downloaded and loaded data locally, we can now initialise the data adapter with the data and 
    # feed data to our optimisation framework via our marlin data feed.

    # Build the MARLIN data feed
    global data_feed_
    global data_feed_label
    print ("Initialising data feed.")
    data_feed_ = MarlinDataStreamer()
    data_feed_label = MarlinDataStreamer()
    
    # initilise the simulation datafeeder with downloaded data in data_adapter
    data_feed_.init_data(data_adapter.simulation_data, data_adapter.simulation_index)
    
    data_feed_label.init_data(data_adapter.signature_data, data_adapter.signature_index)


#   ---------------------------------------
#
#   Data Download / Load
#
#   ---------------------------------------



# do we have the waveform data?
ss_id = sim_ids[0]
sim_load = False
if os.path.isfile(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/data/adapters/{ss_id}.da'):
    sim_load = True

# download_data()
if command == True or len(sim_ids)>0:
    rprint ("Downloading data.")
    if sim_load:
        load_data()
    else:
        download_data()
    #maybe add load here to save time...if data file already downlaoded
else:
    rprint ("Loading data.")
    load_data()
    rprint ("Loading data...Done")

# if command == False:
#     data_adapter.build_game()


print ("sig")
print (data_adapter.signature_index)
print ("sim")
print (data_adapter.simulation_index)




rprint ("Building Data Feed.")
build_feed()
rprint ("Building Data Feed...Done")


# --- Is derived data structure already available?
import os.path
data_avail = False
#---------------------------------------------------------
#
# Using/Build Derived Data Structures
#
#---------------------------------------------------------

data_adapter.build_derived_data(n_fft=8192)
print ("Derived data for simulation...building")


for snapshot in data_feed_:
    
    s_id = snapshot.meta_data['snapshot_id']
    print (f'active s id : {s_id}')
    if not os.path.isfile(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/data/adapters/{s_id}.da'):
        
        print (f'Building derived data feed structure {s_id}')
        logging.critical(f'Building derived data feed structure {s_id}')
        snapshot_derived_data = data_adapter.derived_data.build_derived_data(simulation_data=snapshot, sample_delta_t=1.0, f_min = 130000, f_max = 150000)
        data_adapter.derived_data.build_band_energy_profile(sample_delta_t=0.5, simulation_data=snapshot,discrete_size = 100)
    else:
        data_avail = True
        print ("derived data already available.")
    # with open(f'{s_id}_.der', 'wb') as f:  # open a text file
    #     pickle.dump(snapshot_derived_data, f) # serialize the list
    

if not data_avail:
    with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/data/adapters/{s_id}.da', 'wb') as f:  # open a text file
        pickle.dump(data_adapter.derived_data, f) # serialize the list


print (f'data : {data_avail}')
tmp_derived_data = None

if data_avail:
    
    print ("Loading data as saved data available")
    data_adapter.derived_data = None
    with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/data/adapters/{s_id}.da', 'rb') as f:  # open a text file
        tmp_derived_data = pickle.load(f) 
        data_adapter.derived_data = tmp_derived_data
        
if data_adapter.derived_data == None:
    print ("Crashing. No derived data available.")
    exit()


# labelled data XR   
print ("xr start")
data_adapter.derived_data.build_xr_data()
print ("xr built")
# print (data_adapter.derived_data)
# application.derived_data = data_adapter.derived_data
application.derived_data = data_adapter.derived_data 
application.data_feed = data_feed_




print ("-----")
print (data_feed_)
print (application.derived_data)

# ------------------------------------------------------------------
#
#   Bot(s) download for forward testing
#
# ------------------------------------------------------------------
if command == True and bulk == False:
    print ("Running Bot")
    print ("Loading bot")
    bot_dir = "/home/vixen/rs/dev/marlin_hp/marlin_hp/bots"
    bot_path = f'{bot_dir}/{bot_id}.vixen'
    print (bot_path)
    bot = load_bot(bot_path)
    application.loaded_bots[bot_id] = bot
    application.mode = 1
    



#------------------------------------------------------------------
#
# World and Data Initialised. Let's play the game.
#
#------------------------------------------------------------------

marlin_game = IdentGame(application, optimisationDataManager, activation_level = my_activation_level)


if application.mode == 0:
    rprint("*** START GAME ***")
    marlin_game.play()
    rprint("*** GAME OVER ***")

if application.mode == 1:
    rprint("*** START BOT ***")
    marlin_game.run_bot()
    

# marlin_game = GameSim(application, optimisationDataManager)
# rprint("*** START GAME ***")
# marlin_game.play()
# rprint("*** GAME OVER ***")