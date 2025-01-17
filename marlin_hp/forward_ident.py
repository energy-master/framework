#!/usr/local/bin/python3

"""
=======================================================================================================
forward_ident.py
======================
Written by Rahul Tandon. Copyright Rahul Tandonß

===v1.0===
A python script to:
1. read in acoustic snapshot ids
2. download acoustic data
3. build marlin derived data
4. run features against derived data
5. connect to ident_softmax
5. output:
    1. spectrogram w/energy and other derived profiles
    2. decision list

=======================================================================================================
"""


root_dir = "/home/vixen/rs/dev/marlin_hp/marlin_hp"

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

# sys.path.append('/home/vixen/rs/dev/ident_softmax/ident_softmax')
# from ident_softmax import *

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

# --- IDent Live Application Game ---
# Import the game and application classes.
from game import IdentGame
from ident_application import *
from utils import *

# --------------------------------------------------------------
# --- Imports END ---                                          |
# --------------------------------------------------------------

# --------------------------------------------------------------
# --- BUILD APPLICATION ---                                          |
# --------------------------------------------------------------


# define data load path !- Don't add trailing "/" AND different path for sim and sig
simulation_data_path = "/home/vixen/rs/dev/marlin_hp/marlin_hp/data/sim"
signature_data_path = "/home/vixen/rs/dev/marlin_hp/marlin_hp/data/sig"


 # --- APPLICATION CONFIGURATION ---
# open environment file
load_dotenv()
config = dotenv_values(f'{root_dir}/config_f.env')

config_fp = config['CONFIG_FILE_PATH']
with open(f'{root_dir}/{config_fp}', 'r') as config_f:
    app_config = json.load(config_f)

# Add Application and Data paths to system path
app_path = config['APP_DIR']
sys.path.insert(0, app_path)

data_path = config['DATA_DIR']
working_path = config['WORKING_DIR']
features_path = config['FEATURE_DIR']
out_path = config['OUT_DIR']

# required for librosa
NUMBA_CACHE_DIR = os.path.join(
    '/', 'home', 'vixen', 'rs', 'dev', 'marlin_hp', 'marlin_hp', 'cache')
os.environ['NUMBA_CACHE_DIR'] = NUMBA_CACHE_DIR

# ----------------------------------------------------------------------------
# --- INPUT PARAMETERS -------------------------------------------------------
# ----------------------------------------------------------------------------

batch_file_names = []
batch_run_ids = []
# Input data file (Rules apply : YYYYMMDD_HHMMSS_FFF.wav)
run_id = sys.argv[1]

# Search target (e.g. harbour_porpoise)
target = sys.argv[2]

# Location
location_str = sys.argv[3]

# User UID ( provided by MARLIN )
user_uid = sys.argv[4]

# Activation level of probability distribution function
user_activation_level = sys.argv[5]

# Ratio of features/bots above activation energy. Used in softmax.
user_threshold_above_e = sys.argv[6]

# Number of features (>1000)
number_features = sys.argv[7]

# Similarity of structure built by features (no longer is use)
user_similarity_threshold = sys.argv[8]

# Feature versions (2_0_0/3_0_0)
feature_version = sys.argv[9]

# Feature/bot birth times
time_version_from = ""
time_version_to = ""
update_features = -1
if len(sys.argv) >= 11:
    time_version_from = f'{sys.argv[10]} {sys.argv[11]}'
if len(sys.argv) >= 12:
    time_version_to = f'{sys.argv[12]} {sys.argv[13]}'
    update_features = sys.argv[14]

sim_ids = []
# sim ids
for i in range(15,len(sys.argv)):
    sim_ids.append(sys.argv[i])

if int(update_features) == -1:
    update_features = False
if int(update_features) == 1:
    update_features = True

forwards_nfft = 32768
forwards_min_f = 10
forwards_max_f = 500
forwards_dd_delta_t = 1.0
forwards_dd_delta_f = 20

# Create the data adapter
limit = 200
simulation_data_path = f'{working_path}'
data_adapter = MarlinData(load_args={'limit': limit})

# Download the snapshot data files
location = []
location.append(location_str)

data_adapter.download_simulation_snapshots(load_args={ 'location':location, 'ss_ids' : sim_ids})

# Build data streamer
data_feed = MarlinDataStreamer()
data_feed.init_data(data_adapter.simulation_data,
                    data_adapter.simulation_index)


# Build / Load derived data
all_wf = []
saved_dd = []
sample_rate = 0
for snapshot in data_feed:
    all_wf.append(snapshot.frequency_ts_np) 
    snapshot_derived_data = None
    s_id = snapshot.meta_data['snapshot_id']
    print (snapshot.meta_data)
    sample_rate  = snapshot.meta_data['sample_rate']
    print (f'Searching for derived data : {s_id} ...')
    if not os.path.isfile(f'{working_path}/{s_id}.da'):
        print (f'...not found so building for {s_id}.')
        data_adapter.derived_data = None
        data_adapter.build_derived_data(n_fft=forwards_nfft)
        snapshot_derived_data = data_adapter.derived_data.build_derived_data(
            simulation_data=snapshot,  f_min=forwards_min_f, f_max=forwards_max_f)
        
        print(data_adapter.derived_data)
        
        data_adapter.derived_data.ft_build_band_energy_profile(
            sample_delta_t=forwards_dd_delta_t, simulation_data=snapshot, discrete_size=forwards_dd_delta_f)
        
        data_adapter.multiple_derived_data[s_id] = data_adapter.derived_data
        derived_data_use = data_adapter.derived_data
        
        with open(f'{working_path}/{s_id}.da', 'wb') as f:  # open a text file
            # serialize the list
            pickle.dump(data_adapter.derived_data, f)
            
        print (f'{s_id} derived data structure built.')

        
    else:
        print ("We have derived data.")
        tmp_derived_data = None
        with open(f'{working_path}/{s_id}.da', 'rb') as f:  # open a text file
            load_start = time.time()
            
            tmp_derived_data = pickle.load(f)
        
        data_adapter.derived_data = None
        data_adapter.derived_data = tmp_derived_data
        print(data_adapter.derived_data)
        
        data_adapter.multiple_derived_data[s_id] = tmp_derived_data
        
        dur = time.time()-load_start
        print(f'Time to load MARLIN data [active_ssid] -> {dur}')
        


custom_waveform = np.concatenate(all_wf)

algo_setup = AlgorithmSetup(config_file_path=f'{app_path}/config.json')

#--- update sim configs here ---

#-------------------------------

application = SpeciesIdent(algo_setup)
application.ss_ids = sim_ids
application.mode = 1
application.multiple_data = 1

# for env_pressure in marlin_game.game.data_feed:
application.derived_data = data_adapter.derived_data
application.data_feed = data_feed
application.multiple_derived_data = data_adapter.multiple_derived_data

# ------------------------------------------------------------------
#
#   Bot(s) download for forward testing
#
# ------------------------------------------------------------------

print('Loading features / bots.')

num_loaded = application.load_bots(
            target, version=feature_version, version_time_from=time_version_from,  version_time_to=time_version_to, bot_dir=features_path, number_features=number_features, update=update_features, env=target, root_path = root_dir)

print (f' {num_loaded} loaded.')

# ------------------------------------------------------------------
#
# World and Data Initialised. Let's play the game.
#
# ------------------------------------------------------------------

marlin_game = IdentGame(
    application, None, activation_level=user_activation_level)
marlin_game.game_id = f'{user_uid}_{run_id}'



feature_f = {}


# Initial conditions
frequency_activity = []
for feature in list(application.loaded_bots.values()):
    # print (feature.dNA[0].genome)
    for k, v in feature.dNA.items():
        for kg, vg in v.genome.items():
            for kgg, vgg in vg.genome.items():
                # if 'frequency_index' in vgg:
                
                if hasattr(vgg, 'frequency_index'):
                    idx = vgg.frequency_index
                    
                    f = application.derived_data.min_freq + \
                        (idx * (application.derived_data.index_delta_f))
                    feature_f[feature.name] = f
                    frequency_activity.append(f)
                else:
                    f = vgg.frequency
                    feature_f[feature.name] = f
                    frequency_activity.append(f)
                    

distributed_list = shape_input(feature_f,500)

# Build initial feature frequency distribution plot
plot_hist(frequency_activity,
            f'{out_path}/f_d_{marlin_game.game_id}_init_all.png')

# Update the loaded bots
marlin_game.game.update_bots(
    bot_dir=features_path, feature_list=distributed_list)

frequency_activity = []
for feature in list(application.loaded_bots.values()):
    
    for k, v in feature.dNA.items():
        for kg, vg in v.genome.items():
            for kgg, vgg in vg.genome.items():
                # if 'frequency_index' in vgg:
                if hasattr(vgg, 'frequency_index'):
                    idx = vgg.frequency_index
                    
                    f = application.derived_data.min_freq + \
                        (idx * (application.derived_data.index_delta_f))
                    feature_f[feature.name] = f
                    frequency_activity.append(f)
                else:
                    f = vgg.frequency
                    feature_f[feature.name] = f
                    frequency_activity.append(f)

# Plot prescribed f distribution
plot_hist(frequency_activity,
            f'{out_path}/f_d_{marlin_game.game_id}_reshaped_all.png')

marlin_game.active_features = {}

marlin_game.run_bots(out_path=out_path)

# ------- Softmax API ------------
softmax_data = {
    
    "target" : target,
    "activation_threshold" : user_activation_level,
    "threshold_above_activation": user_threshold_above_e,
    "energies": marlin_game.bulk_energies,
    "times": marlin_game.bulk_times,
    "similarity_factor": user_similarity_threshold
}

print("Sending to Softmax API")
softmax_key = "key1"
headers = {}
softmax_url = 'https://vixen.hopto.org/rs/api/v1/data/softmax'
headers = {'Authorization': softmax_key, 'Accept': 'application/json', 'Content-Type': 'application/json'}
r = requests.post(softmax_url, data=json.dumps(softmax_data), headers=headers)

softmax_results = r.json()

# ------- Softmax API ------------

hits = []


softmax_return_data = json.loads(softmax_results['result'][0])
decisions = softmax_return_data['decisions']
ratio_active = softmax_return_data['r_active']
avg_energies = softmax_return_data['avg_energies']
pc_above_tracker = softmax_return_data['pc_above_tracker']
number_decisions = len(decisions)
print (f'{number_decisions} made.')

#! update
# update_run(filename,12)
# update_run(filename,12.1)


#! update
# update_run(filename,12.2)

if len(marlin_game.bulk_times) > 2:
    # print('build spec')
    build_spec_upload(sample_rate, marlin_game.game_id, hits=hits, decisions=decisions, peak=ratio_active,
                        avg=avg_energies, times=marlin_game.bulk_times, pc_above_e=pc_above_tracker, f=[], full_raw_data=custom_waveform)

#! update
# update_run(filename,12.4)
with open(f'{out_path}/decisions_{marlin_game.game_id}.json', 'w') as fp:
    json.dump(decisions, fp)

#! update
# update_run(filename,13)

# --- NO EDIT END ---
