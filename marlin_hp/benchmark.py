



import os, sys
import librosa
import random, json
from datetime import datetime, timedelta
from datetime import datetime as dt
from datetime import timedelta, timezone
import pickle
from dotenv import load_dotenv, dotenv_values
from typing import List, Dict

import math, statistics

from benchmark_config import *


load_dotenv()
config = dotenv_values("/home/vixen/rs/dev/marlin_hp/marlin_hp/marlin_hp.env")

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


from game import *




# --------------------------------------------------------------
# --- Layer 3 Class ---                                          |
# --------------------------------------------------------------

class Layer_Three(object):
    def __init__(self, activation_level):
        self.activation_level = activation_level
        self.decisions = []
    def run_layer(self,energy_data, time_data):
        # print (time_data)
     
        number_frames = len(time_data)
        print (f'Number frames : {number_frames}')
        
        for frame_count in range(0,number_frames-1):
            expression_list = []
            for feature, value in energy_data.items():
                feature_expression = value[frame_count]
                #print (f'ex: {feature_expression}')
                expression_list.append(feature_expression)
            
            
            average_energy = statistics.mean(expression_list)
            if average_energy > (self.activation_level):
                self.decisions.append({'time': time_data[frame_count], 'decision': 'ident'})
        number_decisions = len(self.decisions)
        print (f' {number_decisions} made from {number_frames} frames.')
        print (self.decisions)

# --------------------------------------------------------------
# --- Benchmark Class ---                                          |
# --------------------------------------------------------------

class BenchmarkRun(object):
    def __init__(self, config : Dict[str,str] = None):
        self.config = config
        self.data = None
        self.labels = None
        
    def add_run_data(self, epoch_id : str = None, data : Dict[str, str] = None):
        self.data.extend(data)
        self.epoch_id = epoch_id
    
    def add_xr_data(self, xr_data, reference_time):
        self.xr_data = xr_data
    
    def run_xr_data(self, label_data):
        
        for decision in self.data:
            start_time = decision['time']
            
    
    def report(self):
        pass
        

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
      
      
      
def load_bot(bot_path):
    print ("loading...")
    print (bot_path)
    file_ptr = open(bot_path, 'rb')
    bot = pickle.load(file_ptr)
    print(bot)
    return bot     
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
            print (bot_path)
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
  



#from marlin_bot_run import AlgorithmSetup, SpeciesIdent
#import marlin_bot_run
# import marlin data adapter
sys.path.append('/home/vixen/rs/dev/marlin_data/marlin_data')
from marlin_data import *

#--------------------------------------------------------------------------------
#
#   Run each file in the benchmark and record decisions xr with labels
#
#--------------------------------------------------------------------------------

benchmark = BenchmarkRun()

for idx,data in bench_data_files.items():

    # get raw_data and sample_rate
    # target file for raw data
    file_path = f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_data/{idx}.wav'
    raw_data, sample_rate = librosa.load(file_path,  sr=int(sample_rate))
    print (file_path)
    
    # -- META DATA
    # get sample end time
    start_time = "140822_155229.000000"
    start_t_dt = dt.strptime(start_time, '%y%m%d_%H%M%S.%f')
    duration_s = len(raw_data)/sample_rate
    start_t_ms = int(start_t_dt.timestamp()) * 1000
    end_t_dt = start_t_dt + timedelta(seconds=duration_s)
    end_t_ms = int(end_t_dt.timestamp()) * 1000
    end_t_f = end_t_dt.strftime('%y%m%d_%H%M%S.%f')
    print (f'Number of seconds : {duration_s}')
    print (start_t_dt, end_t_dt)
    print (start_t_ms, end_t_ms)
    print (end_t_f)



    meta_data = {
        "snapshot_id":idx,
        "data_frame_start": data[1],
        "data_frame_end": end_t_f,
        "listener_location": {"latitude": 0, "longitude": 0}, "location_name"
            : "67149847", "frame_delta_t": 10, "sample_rate": sample_rate, "marlin_start_time": 1408719149000,
        "marlin_end_time": 1408719159000
        }


    # --- now we have the raw data, we need to build the derived data object using marlin_data

    # write the file to the tmp folder

    tmp_stream = f'streamedfile_{idx}.dat'
    tmp_meta = f'metadata_{idx}.json'


    raw_data.tofile(f'ext_tmp/{tmp_stream}')
    with open(f'ext_tmp/{tmp_meta}', 'w') as f:
        json.dump(meta_data, f)
        

    # create the data adapter
    simulation_data_path = f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp'
    data_adapter = MarlinData(load_args={'limit' : 10})

    # load uploaded data
    limit = 2
    r = data_adapter.load_from_path(load_args={'load_path' : simulation_data_path, "snapshot_type":"simulation", "limit" : limit})

    data_feed = MarlinDataStreamer()
    data_feed.init_data(data_adapter.simulation_data, data_adapter.simulation_index)


    print ("sim")
    print (data_adapter.simulation_index)

    sim_ids = []
    sim_ids = [idx]

    s_id = idx
    data_adapter.build_derived_data(n_fft=8192)
    data_avail = False
    for snapshot in data_feed:
        # print (snapshot.meta_data)
        s_id = snapshot.meta_data['snapshot_id']
        print (f'{snapshot.meta_data}')
        if not os.path.isfile(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{s_id}.da'):
            
            print (f'Building derived data feed structure {s_id}')
            
            snapshot_derived_data = data_adapter.derived_data.build_derived_data(simulation_data=snapshot, sample_delta_t=1.0, f_min = 130000, f_max = 150000)
            data_adapter.derived_data.build_band_energy_profile(sample_delta_t=0.5, simulation_data=snapshot,discrete_size = 100)
        else:
            data_avail = True
            print ("Derived data already available.")
        # # with open(f'{s_id}_.der', 'wb') as f:  # open a text file
        # #     pickle.dump(snapshot_derived_data, f) # serialize the list




    if not data_avail:
        with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{s_id}.da', 'wb') as f:  # open a text file
            pickle.dump(data_adapter.derived_data, f) # serialize the list


    if data_avail:
        
        print ("Loading data as saved data available.")
        data_adapter.derived_data = None
        with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{s_id}.da', 'rb') as f:  # open a text file
            tmp_derived_data = pickle.load(f) 
            data_adapter.derived_data = tmp_derived_data
            

    # ---- Data has been initialised -----

    algo_setup = AlgorithmSetup(config_file_path="/home/vixen/rs/dev/marlin_hp/marlin_hp/config.json")

    application = SpeciesIdent(algo_setup)
    application.ss_ids = sim_ids

    application.derived_data = data_adapter.derived_data 
    application.data_feed = data_feed

    # ------------------------------------------------------------------
    #
    #   Bot(s) download for forward testing
    #
    # ------------------------------------------------------------------
    application.load_bots(target)
    application.mode = 1


    #------------------------------------------------------------------
    #
    # World and Data Initialised. Let's play the game.
    #
    #------------------------------------------------------------------
    run_time_data = None
    run_energy_data = None
    marlin_game = IdentGame(application, None, activation_level = 0.7)
    if application.mode == 1:
        print("*** START BOT ***")
        run_energy_data, run_time_data = marlin_game.run_bot()



    #------------------------------------------------------------------
    #
    # Evaluate outptut as decisions
    #
    #------------------------------------------------------------------

    layer_three = Layer_Three(activation_level=0.1)
    layer_three.run_layer(run_energy_data, run_time_data)

    benchmark.add_run_data(idx, layer_three.decisions)


#------------------------------------------------------------------
#
# Benchmark run
#
#------------------------------------------------------------------












