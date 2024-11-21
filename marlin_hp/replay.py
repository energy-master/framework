



import os, sys
import librosa
import random, json
from datetime import datetime, timedelta
from datetime import datetime as dt
from datetime import timedelta, timezone
import pickle
from dotenv import load_dotenv, dotenv_values

from benchmark_config import *
print ('importing io')
from io_custom import *



load_dotenv()
config = dotenv_values("/home/vixen/rs/dev/marlin_hp/marlin_hp/marlin_hp.env")

# print (config)

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
    # print ("loading...")
    # print (bot_path)
    file_ptr = open(bot_path, 'rb')
    bot = pickle.load(file_ptr)
    # print(bot)
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
        print (url)
        print (post_data)
        
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
                # print (bot)
                self.loaded_bots[bot_id] = bot
            except:
                error = True
                # print (f'error loading {bot_id}')
                
            if  error == False:
                number_loaded+=1
                if number_loaded > float(number_features):
                    break
                # print (f'success loading {bot_id}')
            
        
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

filename    =   sys.argv[1]
target      =   sys.argv[2]
location    =   sys.argv[3]
user_uid    =   sys.argv[4]
user_activation_level = sys.argv[5]
user_threshold_above_e = sys.argv[6]
number_features = sys.argv[7]
user_similarity_threshold = sys.argv[8]
new_game_id = sys.argv[9]
filename_ss_id = filename.split('_')[0]

shell_config = {}
shell_config['filename']    = sys.argv[1]
shell_config['target']      = sys.argv[2]
shell_config['location']    = sys.argv[3]
shell_config['user_uid']    = sys.argv[4]
shell_config['user_activation_level'] = sys.argv[5]
shell_config['user_threshold_above_e'] = sys.argv[6]
shell_config['number_features'] = sys.argv[7]
shell_config['similarity_threshold'] = sys.argv[8]
shell_config['new_game_id'] = sys.argv[9]


# sample_rate =   sys.argv[4]

# get raw_data and sample_rate
# target file for raw data

# create new run in db
send_new_run(new_game_id, target, user_uid, location, json.dumps(shell_config))


file_path = f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_data/{filename_ss_id}.wav'
raw_data, sample_rate = librosa.load(file_path,  sr=int(sample_rate))

# -- META DATA
# get sample end time
start_time = "140822_155229.000000"
start_time = "010101_000000.000000"
start_t_dt = dt.strptime(start_time, '%y%m%d_%H%M%S.%f')
duration_s = len(raw_data)/sample_rate
start_t_ms = int(start_t_dt.timestamp()) * 1000
end_t_dt = start_t_dt + timedelta(seconds=duration_s)
end_t_ms = int(end_t_dt.timestamp()) * 1000
end_t_f = end_t_dt.strftime('%y%m%d_%H%M%S.%f')

print (f'Sample Rate : {sample_rate}')
print (f'Number of seconds : {duration_s}')
print (start_t_dt, end_t_dt)
print (start_t_ms, end_t_ms)
print (end_t_f)



meta_data = {
    "snapshot_id":filename_ss_id,
    "data_frame_start": start_time,
    "data_frame_end": end_t_f,
    "listener_location": {"latitude": 0, "longitude": 0}, "location_name"
        : "67149847", "frame_delta_t": 10, "sample_rate": sample_rate, "marlin_start_time": 1408719149000,
    "marlin_end_time": 1408719159000
    }


# --- now we have the raw data, we need to build the derived data object using marlin_data

# write the file to the tmp folder

tmp_stream = f'streamedfile_{filename_ss_id}.dat'
tmp_meta = f'metadata_{filename_ss_id}.json'


raw_data.tofile(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{tmp_stream}')
with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{tmp_meta}', 'w') as f:
    json.dump(meta_data, f)
    

# create the data adapter
simulation_data_path = f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp'
data_adapter = MarlinData(load_args={'limit' : 10})

# load uploaded data
sim_ids = []
sim_ids = [filename_ss_id]
limit = 2
r = data_adapter.load_from_path(load_args={'load_path' : simulation_data_path, "snapshot_type":"simulation", "limit" : limit,  'ss_ids' : sim_ids})

data_feed = MarlinDataStreamer()
data_feed.init_data(data_adapter.simulation_data, data_adapter.simulation_index)


print ("sim")
print (data_adapter.simulation_index)







s_id = filename_ss_id
data_adapter.build_derived_data(n_fft=8192)
data_avail = False
for snapshot in data_feed:
    # print (snapshot.meta_data)
    s_id = snapshot.meta_data['snapshot_id']
    # print (f'{snapshot.meta_data}')
    if not os.path.isfile(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{s_id}.da'):
        update_run(new_game_id,1)
        print (f'Building derived data feed structure {s_id}')
        
        snapshot_derived_data = data_adapter.derived_data.build_derived_data(simulation_data=snapshot,  f_min = 115000, f_max = 145000)
        data_adapter.derived_data.ft_build_band_energy_profile(sample_delta_t=0.01, simulation_data=snapshot,discrete_size = 500)
    else:
        update_run(new_game_id,2)
        data_avail = True
        print ("Derived data already available.")
    # # with open(f'{s_id}_.der', 'wb') as f:  # open a text file
    # #     pickle.dump(snapshot_derived_data, f) # serialize the list




# if not data_avail:
#     update_run(new_game_id,3)
#     print ('saving')
#     with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{s_id}.da', 'wb') as f:  # open a text file
#         pickle.dump(data_adapter.derived_data, f) # serialize the list



# if data_avail:
#     update_run(new_game_id,4)
#     print ("Loading data as saved data available.")
#     data_adapter.derived_data = None
#     with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{s_id}.da', 'rb') as f:  # open a text file
#         tmp_derived_data = pickle.load(f) 
#         data_adapter.derived_data = tmp_derived_data
        

# ---- Data has been initialised -----

# print (data_adapter.derived_data.index_delta_f)
# print (data_adapter.derived_data.min_freq)
# print (data_adapter.derived_data.min_freq + (12 * (data_adapter.derived_data.index_delta_f)))

# exit()

game_file_name = f'/home/vixen/html/rs/ident_app/ident/brahma/out/game_{filename}.game'

with open(game_file_name, 'rb') as f:
    marlin_game = pickle.load(f)
    
# algo_setup = AlgorithmSetup(config_file_path="/home/vixen/rs/dev/marlin_hp/marlin_hp/config.json")

# application = SpeciesIdent(algo_setup)
# application.ss_ids = sim_ids

# # application.derived_data = data_adapter.derived_data 
# application.data_feed = data_feed

# ------------------------------------------------------------------
#
#   Bot(s) download for forward testing
#
# ------------------------------------------------------------------
# application.load_bots(target)
# application.mode = 1


#------------------------------------------------------------------
#
# World and Data Initialised. Let's RE - play the game.
#
#------------------------------------------------------------------


    
# marlin_game = IdentGame(application, None, activation_level = user_activation_level)
marlin_game.game_id = new_game_id
print (f'marlin_game_id : {marlin_game.game_id}')
# set new game id

from layer_three import *
from utils import *

if marlin_game.game.mode == 1:
    
    update_run(new_game_id,5)
    print("*** START BOT ***")
    
    # show init f dist
    frequency_activity = []
    for feature in list(marlin_game.game.loaded_bots.values()):
        # print (feature.dNA[0].genome)
        for k,v in feature.dNA.items():
            for kg,vg in v.genome.items():
                for kgg, vgg in vg.genome.items():
                    # if 'frequency_index' in vgg:
                    idx = vgg.frequency_index
                    f = marlin_game.game.derived_data.min_freq + (idx *  (marlin_game.game.derived_data.index_delta_f))
                    frequency_activity.append(f)
    
    
    filename_ = f'/home/vixen/html/rs/ident_app/ident/brahma/out/f_d_{marlin_game.game_id}_init_all.png'
    plot_hist(frequency_activity, filename_)
    # print (filename)
    
    # marlin_game.run_bot()
    # marlin_game.run_bot()
    
    # save game
    # with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/game_{filename}.game', 'wb') as f:
    #     pickle.dump(marlin_game, f)
    # save game
    with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/game_{new_game_id}.game', 'wb') as f:
        pickle.dump(marlin_game, f)
    
    
    #write all decisions to json
    update_run(new_game_id,11)
    
    layer_3 = Layer_Three(activation_level = user_activation_level,threshold_above_activation = user_threshold_above_e, derived_data = marlin_game.game.derived_data, similarity_threshold = user_similarity_threshold, run_id=filename, target=target)
    freq = layer_3.run_layer(marlin_game.bulk_energies, marlin_game.bulk_times,active_features=marlin_game.active_features, all_features=list(marlin_game.game.loaded_bots.values()) )
    
    # print (marlin_game.bulk_times)
    
    with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/decisions_{marlin_game.game_id}.json', 'w') as fp:
        json.dump(layer_3.decisions, fp)

    update_run(new_game_id,12)

    hits = []
    decisions = layer_3.decisions
    
    for env_pressure in marlin_game.game.data_feed:
        # print (env_pressure)
        build_spec_upload(env_pressure, marlin_game.game_id, hits = hits, decisions = decisions, peak=layer_3.peak_energies, avg=layer_3.avg_energies, times=marlin_game.bulk_times, pc_above_e = layer_3.pc_above_tracker, f = freq)
             

    # dump group energies and times with new filename
    
    with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/group_energies_{marlin_game.game_id}.json', 'w+') as f:
        json.dump(marlin_game.bulk_energies,f)  
         
    # with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/group_times_{self.game.ss_ids[0]}.json', 'w+') as f:
    with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/group_times_{marlin_game.game_id}.json', 'w+') as f:
    
        json.dump(marlin_game.bulk_times,f)  
    
    update_run(new_game_id,13)
    
   
    
    








