

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
from report_procedures import *
import numpy as np

from scipy import signal

from scipy.fft import fftshift

import matplotlib.pyplot as plt

load_dotenv()
config = dotenv_values("/home/vixen/rs/dev/marlin_hp/marlin_hp/marlin_hp.env")

if (len(sys.argv) > 1):
    study_id = sys.argv[1]
    min_f = float(sys.argv[2])
    max_f = float(sys.argv[3])
    
# git test  - 
sim_ids = []
for arg in range(4,len(sys.argv)):
    sim_ids.append(sys.argv[arg])


active_nfft = 32768
run_delta_t = 0.5
derived_delta_t = 1
location = ['brixham']

# print (sim_ids, study_id)

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

sys.path.append('/home/vixen/rs/dev/marlin_data/marlin_data')
from marlin_data import *





# sim_ids = ["331536168117870546723100"] # "10065410156183055710193", "298448815225760525793106","963118742699735308517278","27375678350083866014024","553063846482917121543419", "607275917932749114463656","872949322189341025963541","21568196775422569759630","360852791896317614623842","50453828686617928438686"]
# define data load path !- Don't add trailing "/" AND different path for sim and sig
simulation_data_path = "/home/vixen/rs/dev/marlin_hp/marlin_hp/data/sim"
report_out_path = "/home/vixen/html/rs/ident_app/ident/brahma/report"
# data load routine    
def load_data(data_adapter):
    # Load data into the marlin data adapter from a local source
    #   -params-
    #   load_path : path to local rep of serial data
    #   limit : max number of downlaods
    #   snapshot_type : type of snapshot [ simulation | signature ]
    limit = 10
    #r = data_adapter.load_from_path(load_args={'load_path' : simulation_data_path, "snapshot_type":"signature", "limit" : limit})
    # for ss_id in sim_ids:
    #     if os.path.isfile(f'streamedfile_{ss_id}.dat'):
    #         r = data_adapter.load_from_path(load_args={'load_path' : simulation_data_path, "snapshot_type":"simulation", 'ss_ids' : sim_ids,"limit" : limit})
    # else:
    
    # download all data from server
    # print (sim_ids)
    data_adapter.download_simulation_snapshots(load_args={'ss_ids' : sim_ids, 'location' : location})
            

# =================================== LOAD DATA ====================================================



# Init data adapter (marlin adapter)
data_available = False

limit = 100
data_adapter = None
data_adapter = MarlinData(load_args={'limit' : limit})


#check if data already available
data_available = load_data(data_adapter)

data_feed = None
data_feed = MarlinDataStreamer()

# initilise the simulation datafeeder with downloaded data in data_adapter
data_feed.init_data(data_adapter.simulation_data, data_adapter.simulation_index)

data_adapter.derived_data = None
data_required = []
for active_ssid in sim_ids:

    if os.path.isfile(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/data/adapters/{active_ssid}.da'):
        # derived data present
        with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/data/adapters/{active_ssid}.da', 'rb') as f:  # open a text file
            print (f'Building derived data : {active_ssid}')
        
            tmp_derived_data = pickle.load(f) 
            #tmp_derived_data.get_max_f_index()
            data_adapter.derived_data = tmp_derived_data
            #print(tmp_derived_data.fast_index_energy_stats)
            max_frequency_index = 0
            for f_index, value in tmp_derived_data.fast_index_energy_stats.items():
                max_frequency_index = max(f_index, max_frequency_index)
            data_adapter.multiple_derived_data[active_ssid] = tmp_derived_data
            print (f'max frequency index : {max_frequency_index}')
            
    else:
            data_required.append(active_ssid)
        
            
            
print (data_required)

if len(data_required) > 0:

    for snapshot in data_feed:
        
        if snapshot.meta_data['snapshot_id'] in data_required:
            print ('building...')
            data_adapter.derived_data = None
            active_samplerate = snapshot.meta_data['sample_rate']
            active_nfft = int((active_samplerate/2)) + 1
            f_res = math.ceil(snapshot.meta_data['sample_rate'] / active_nfft)
            
            data_adapter.build_derived_data(n_fft=active_nfft)
            snapshot_derived_data = data_adapter.derived_data.build_derived_data(simulation_data = snapshot, f_min = 10, f_max = 500)
            data_adapter.derived_data.ft_build_band_energy_profile(sample_delta_t=derived_delta_t, simulation_data = snapshot, discrete_size=f_res )
            # print summary
            print(data_adapter.derived_data)
            data_adapter.multiple_derived_data[snapshot.meta_data['snapshot_id']] = data_adapter.derived_data
            working_ssid = snapshot.meta_data['snapshot_id']
        
            # with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/data/adapters/{working_ssid}_{active_nfft}.da', 'wb') as f:
            #     pickle.dump(data_adapter.derived_data, f)
            
            


# =================================== *********************** ====================================================
# 
# =================================== RUN SCRIPTS AGAINST SS =====================================================



entropy_profile = f'entropy_profile_{study_id}.csv'
entropy_f_profile = f'entropy_freq_profile_{study_id}.csv'
frequency_profile = f'frequency_profile_{study_id}.csv'

with open(f'{report_out_path}/{entropy_profile}', 'w') as f:
    f.write('time,entropy\n')
    
with open(f'{report_out_path}/{entropy_f_profile}', 'w') as f:
    f.write('time,entropy\n')
    
with open(f'{report_out_path}/{frequency_profile}', 'w') as f:
    f.write('time,frequency\n')
    
delta_t = run_delta_t

study_frequency_profile = {}
entropy_list = []

min_f = 0
max_f = 300
delta_f = 50


all_wf = []
sample_rate = 0
for env_pressure in data_feed:
    
    listen_start_idx = 0
    listen_end_idx = 0
    # print (env_pressure.meta_data['snapshot_id'])
    listen_delta_idx = math.floor(delta_t * env_pressure.meta_data['sample_rate'])
    env_pressure_length = env_pressure.frequency_ts_np.shape[0]
    print (f'l : {env_pressure_length}')
    # print (env_pressure.frequency_ts_np)
    
    sample_rate = env_pressure.meta_data['sample_rate']
    energies = []
    times = []
    hits = [] # list of label hits for game mode 1
    idx_iter = 0
    idx = 0
    all_wf.append(env_pressure.frequency_ts_np)
   
    continue
    
    
    while listen_start_idx < (env_pressure_length):
        
        # --- get start & end slice idx ---
        listen_end_idx = listen_start_idx + listen_delta_idx
        slice_start = listen_start_idx
        slice_end = min(listen_end_idx,env_pressure_length-1)

        # --- get datetime ---  # 2014-08-22 15:53:18.500000
        _s = (slice_start / env_pressure.meta_data['sample_rate']) * 1000 # ms 
        iter_start_time =  env_pressure.start_time + timedelta(milliseconds=_s)
        _s = (slice_end / env_pressure.meta_data['sample_rate']) * 1000
        iter_end_time   =  env_pressure.start_time  + timedelta(milliseconds=_s)
        print (f'time vector bounds : {iter_start_time} : {iter_end_time}')
        
        
        
        derived_data = data_adapter.multiple_derived_data[env_pressure.meta_data['snapshot_id']]
        # e_n = grab_entropy_across_f_bins(listen_start_idx, derived_data, env_pressure.meta_data['sample_rate'])
        # entropy_list.append(e_n)
        
        # with open(f'{report_out_path}/{entropy_profile}', 'a+') as f:
        #     f.write(f'{iter_start_time},{e_n} \n')
        
        # e_f_n = grab_kurtosis_at_f_t(2,derived_data,iter_start_time,delta_f)
        # #e_f_n = 0.0
        # # print(e_n)
        # with open(f'{report_out_path}/{entropy_f_profile}', 'a+') as f:
        #     f.write(f'{iter_start_time},{e_f_n} \n')
        
        
        # -- study data
        #build_f_profile(iter_start_time, derived_data, study_frequency_profile)
        f_path = f'{report_out_path}/f_p_{idx}_{study_id}.png'
        build_f_profile_vector(iter_start_time, iter_end_time,derived_data, study_frequency_profile, f_path)
        idx+=1
       
        
        # update listen start idx
        listen_start_idx = listen_end_idx


custom_waveform = np.concatenate(all_wf)

# frequency_hist = calculate_study_frequency_profile(study_frequency_profile)
# entropy_stats = calculate_entropy_stats(entropy_list)

#print (frequency_hist)


# with open(f'{report_out_path}/{frequency_profile}', 'a+') as f:
#     for idx, value in frequency_hist.items():
#         f.write(f'{idx},{value}\n')
  
        
# for k,v in kurtosis_tracker.items():
#     with open(f'{report_out_path}/kurt_{k}_{study_id}.csv', 'w') as f:
#         f.write(f'time,kurtosis\n')
#         for idx, value in enumerate(v):
#             f.write(f'{idx},{value}\n')

#os.system(f'ffmpeg -r 5  -s 1920x1080 -i {report_out_path}/f_p_%d_{study_id}.png -vcodec libx264 -crf 25 -pix_fmt yuv420p {report_out_path}/{study_id}_fp.mp4') 

# =================== REPORT BUILDING ===================



# print (custom_waveform)
# f, t, Sxx = signal.spectrogram(custom_waveform, sample_rate, nfft=2048)
# plt.pcolormesh(t, f, Sxx, shading='gouraud')

# plt.ylabel('Frequency [Hz]')

# plt.xlabel('Time [sec]')
# plt.savefig(f'{report_out_path}/spec_{study_id}.png')

total_time = custom_waveform.shape[0] / sample_rate
print (f'total time : {total_time}')
t = np.arange(0,total_time, 1/sample_rate)


plt.plot(t, custom_waveform)
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.savefig(f'{report_out_path}/wf_{study_id}.png')
plt.close()

n = len(custom_waveform) # length of the signal
k = np.arange(n)
T = n/sample_rate
frq = k/T # two sides frequency range
frq = frq[:len(frq)//2] # one side frequency range

Y = np.fft.fft(custom_waveform)/n # dft and normalization
Y = Y[:n//2]

plt.plot(frq,abs(Y)) # plotting the spectrum
plt.xlabel('Freq (Hz)')
plt.ylabel('|Y(freq)|')
# plt.xlim(20, 1000)
plt.savefig(f'{report_out_path}/dft_{study_id}.png')

