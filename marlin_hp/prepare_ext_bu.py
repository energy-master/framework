



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

s_interval = 5

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

    def load_bots(self, filter_data, version="1_0_0", version_time_from="",version_time_to=""):
        # print (filter_data)
        
        url = 'https://vixen.hopto.org/rs/api/v1/data/features'
        post_data = {'market': filter_data, 'version_time_from' : version_time_from, 'version_time_to' : version_time_to}
        
        
        # print (url)
        # print (post_data)
        
        x = requests.post(url, json = post_data)
        data  = x.json()
        number_loaded = 0
        number_read = 0
        
        versions_list  = version.split('/')
        
        
        for key in data["data"]:
            number_read+=1
            bot_id = key['botID']
            
            bot_dir = "/home/vixen/rs/dev/marlin_hp/marlin_hp/bots"
            bot_path = f'{bot_dir}/{bot_id}.vixen'
            # print (bot_path)
            error = False
            # print (f'loading {version}')
            
            

            try:
                bot = load_bot(bot_path)
                # print (bot)
                # exit()
                
                add = True
                    
                for k,v in bot.dNA.items():
                    for kg,vg in v.genome.items():
                        for kgg, vgg in vg.genome.items():
                            if vgg.condition == 'EnergyProfileFluxIndexPersistent':
                                # print (vgg.condition)
                                add = False
                                continue
                            
                
                
                if hasattr(bot, 'version'):
                    
                    # print (bot)
                    if bot.version not in versions_list:
                        add = False
                        continue
                    else:
                        print (f'v: {bot.version} | {versions_list}')
                        
                
                else:
                    if "1_0_0" != version:
                        add = False
                        continue
                
                if add:
                    print ('adding bot to game')
                    self.loaded_bots[bot_id] = bot
                    number_loaded+=1
                    if number_loaded > float(number_features):
                        break
            except Exception as e:
                error = True
                # print (f'error loading {bot_id} {type(e).__name__}')
                
            if  error == False:
                pass
                # print (f'success loading {bot_id}')
            
            
        
        self.mode = 1
        self.bulk = 1
        print (f'number loaded : {number_loaded}')
        print (f'number read : {number_read}')
        shell_config['number_working_features'] = number_loaded
        
    
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
feature_version = sys.argv[9]
time_version_from = ""
time_version_to = ""
if len(sys.argv) >= 11:
    time_version_from = f'{sys.argv[10]} {sys.argv[11]}'
if len(sys.argv) >= 12:
    time_version_to = f'{sys.argv[12]} {sys.argv[13]}'
   


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
shell_config['feature_version'] = sys.argv[9]
shell_config['time_version_from'] = time_version_from
shell_config['time_version_to'] = time_version_to

# print (shell_config)

# sample_rate =   sys.argv[4]

# get raw_data and sample_rate
# target file for raw data

# create new run in db
# send_new_run(filename, target, user_uid, location, json.dumps(shell_config))


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
limit = 20


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
        update_run(filename,1)
        print (f'Building derived data feed structure {s_id}')
        
        snapshot_derived_data = data_adapter.derived_data.build_derived_data(simulation_data=snapshot,  f_min = 115000, f_max = 145000)
        data_adapter.derived_data.ft_build_band_energy_profile(sample_delta_t=0.01, simulation_data=snapshot,discrete_size = 500)
    else:
        update_run(filename,2)
        data_avail = True
        print ("Derived data already available.")
    # # with open(f'{s_id}_.der', 'wb') as f:  # open a text file
    # #     pickle.dump(snapshot_derived_data, f) # serialize the list




if not data_avail:
    update_run(filename,3)
    print ('saving')
    with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{s_id}.da', 'wb') as f:  # open a text file
        pickle.dump(data_adapter.derived_data, f) # serialize the list



if data_avail:
    update_run(filename,4)
    print ("Loading data as saved data available.")
    data_adapter.derived_data = None
    with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/ext_tmp/{s_id}.da', 'rb') as f:  # open a text file
        tmp_derived_data = pickle.load(f) 
        data_adapter.derived_data = tmp_derived_data
        

# ---- Data has been initialised -----

# print (data_adapter.derived_data.index_delta_f)
# print (data_adapter.derived_data.min_freq)
# print (data_adapter.derived_data.min_freq + (12 * (data_adapter.derived_data.index_delta_f)))

# exit()


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
application.load_bots(target, version=feature_version, version_time_from = time_version_from,  version_time_to = time_version_to)
# exit()
application.mode = 1
# create new run in db
# send_new_run(filename, target, user_uid, location, json.dumps(shell_config))


#------------------------------------------------------------------
#
# World and Data Initialised. Let's play the game.
#
#------------------------------------------------------------------

marlin_game = IdentGame(application, None, activation_level = user_activation_level)
marlin_game.game_id = filename


from layer_three import *
from utils import *

if application.mode == 1:
    
    update_run(filename,5)
    print("*** START BOT ***")
    
    # show init f dist
    frequency_activity = []
    for feature in list(application.loaded_bots.values()):
        # print (feature.dNA[0].genome)
        for k,v in feature.dNA.items():
            for kg,vg in v.genome.items():
                for kgg, vgg in vg.genome.items():
                    # if 'frequency_index' in vgg:
                    idx = vgg.frequency_index
                    f = application.derived_data.min_freq + (idx *  (application.derived_data.index_delta_f))
                    frequency_activity.append(f)
    
    
    filename_ = f'/home/vixen/html/rs/ident_app/ident/brahma/out/f_d_{marlin_game.game_id}_init_all.png'
    plot_hist(frequency_activity, filename_)
    # print (filename)
    
    #get total time:
    
    number_runs = math.floor(duration_s / s_interval)
    delta_idx = s_interval * sample_rate
    
    send_new_run(filename, target, user_uid, location, json.dumps(shell_config))
    end_idx = 0
    
    all_decisions = {}
    
    combined_bulk_energies = {}    
    combined_bulk_times = {}
    combined_active_features = {}
    
    print (f'number_runs {number_runs}')
    
    for run_i in range(0,number_runs):
        
        print (f'running {run_i} iteration')
        if run_i == number_runs:
            break
        sub_filename = f'{filename}_{run_i}'
        send_new_run(sub_filename, target, user_uid, location, json.dumps(shell_config))
        
        start_idx = end_idx
        end_idx = start_idx+delta_idx
        
        marlin_game.active_features = {}
        marlin_game.run_bot_mt(sub_filename=sub_filename, start_idx=start_idx, end_idx=end_idx)
        
        # print (marlin_game.bulk_energies)
        # print (len(marlin_game.bulk_times))
        # print (marlin_game.number_run_idx)
        
        
        for k,v in marlin_game.bulk_energies.items():
            energies_d = v
            for ke, ve in v.items():
                if k not in combined_bulk_energies:
                    combined_bulk_energies[k] = {}
                    
                combined_bulk_energies[k][ke+(run_i*(marlin_game.number_run_idx+1))] = ve
                

        for k,v in marlin_game.bulk_times.items():
            combined_bulk_times[k+(run_i*(marlin_game.number_run_idx+1))] = v
            
        for k,v in marlin_game.active_features.items():
            combined_active_features[k+(run_i*(marlin_game.number_run_idx+1))] = v
        
        # print (marlin_game.bulk_times)
        for k,v in combined_bulk_energies.items():
            print (f'le : {len(v)}')
            break
    
        for k,v in marlin_game.bulk_energies.items():
            print (f'mge : {len(v)}')
            break
        
        # marlin_game.run_bot()
        
        # save game
        # with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/game_{sub_filename}.game', 'wb') as f:
        #     pickle.dump(marlin_game, f)
        
        
        #write all decisions to json
        update_run(sub_filename,11)
        # print (marlin_game.active_features)
        # print (marlin_game.bulk_times)
        # layer_3 = Layer_Three(activation_level = user_activation_level,threshold_above_activation = user_threshold_above_e, derived_data = application.derived_data, similarity_threshold = user_similarity_threshold, run_id=filename, target=target)
        layer_3 = Layer_Three(activation_level = user_activation_level,threshold_above_activation = user_threshold_above_e, derived_data = application.derived_data, similarity_threshold = user_similarity_threshold, run_id=filename, target=target)
        freq = layer_3.run_layer(marlin_game.bulk_energies, marlin_game.bulk_times,active_features=marlin_game.active_features, all_features=list(marlin_game.game.loaded_bots.values()) )

        
        
        
        with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/decisions_{sub_filename}.json', 'w') as fp:
            json.dump(layer_3.decisions, fp)
        
        update_run(sub_filename,12)

        hits = []
        decisions = layer_3.decisions
        a_ratio = layer_3.ratio_active
        print (f't: {len(marlin_game.bulk_times)}')
        print (f'd: {len(layer_3.ratio_active)}')
        print (f'c_t :{len(combined_bulk_times)}')
        # print (f'c_d :{len(combined_bulk_energies)}')
        
        for env_pressure in marlin_game.game.data_feed:
            # print (env_pressure)

            build_spec_upload(env_pressure, sub_filename, hits = hits, decisions = decisions, peak=a_ratio, avg=layer_3.avg_energies, times=marlin_game.bulk_times, pc_above_e = layer_3.pc_above_tracker, f = freq)
                
        
        update_run(sub_filename,13)
    
    
    update_run(filename,12)
    
    # print (combined_bulk_energies)
    
    for k,v in combined_bulk_energies.items():
        print (len(v))
        break
        
    # print (combined_bulk_times)
    # print (len(combined_bulk_times))
    
    marlin_game.bulk_times = combined_bulk_times
    marlin_game.bulk_energies = combined_bulk_energies
    marlin_game.active_features = combined_active_features
    print (marlin_game.active_features)
    
    layer_3 = Layer_Three(activation_level = user_activation_level,threshold_above_activation = user_threshold_above_e, derived_data = application.derived_data, similarity_threshold = user_similarity_threshold, run_id=filename, target=target)
    freq = layer_3.run_layer(marlin_game.bulk_energies, marlin_game.bulk_times, active_features=marlin_game.active_features, all_features=list(marlin_game.game.loaded_bots.values()) )
    # print (len(layer_3.ratio_active))
    # save game
    with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/game_{filename}.game', 'wb') as f:
        pickle.dump(marlin_game, f)
    
    
    with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/decisions_{filename}.json', 'w') as fp:
            json.dump(layer_3.decisions, fp)
    for env_pressure in marlin_game.game.data_feed:
        build_spec_upload(env_pressure, filename, hits = hits, decisions = layer_3.decisions, peak=layer_3.ratio_active, avg=layer_3.avg_energies, times=marlin_game.bulk_times, pc_above_e = layer_3.pc_above_tracker, f = freq)
            
    update_run(filename,13)
        
    
        
        








