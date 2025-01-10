

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




study_id = sys.argv[1]
f_min = float(sys.argv[2])
f_max = float(sys.argv[3])
window_size = int(sys.argv[4])
start_time = float(sys.argv[5])
end_time = float(sys.argv[6])
location_str = (sys.argv[7])
    
    
# git test  - 
sim_ids = []
for arg in range(8,len(sys.argv)):
    sim_ids.append(sys.argv[arg])


active_nfft = int(window_size)#2048 # 32768
run_delta_t = 0.5
derived_delta_t = 1
# location = ['brixham']
location = []
location.append(location_str)
print (location)
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
    #r = data_adapter.load_from_path(load_args={'load_path' : simulation_data_path, "snapshot_type":"simulation", "limit" : limit, 'ss_ids' : sim_ids})
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
            _sid = snapshot.meta_data['snapshot_id']
            print (f'Building {_sid} derived data.')
            data_adapter.derived_data = None
            active_samplerate = snapshot.meta_data['sample_rate']
            active_nfft = int((active_samplerate))
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


if start_time != -1:
    start_index = math.floor(start_time * sample_rate)
    end_index = math.floor(end_time * sample_rate)
    custom_waveform = custom_waveform[start_index:end_index]


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
# f, t, Sxx = signal.spectrogram(custom_waveform, sample_rate,window=signal.blackman(active_nfft), nfft=active_nfft)
# plt.pcolormesh(t, f, Sxx, shading='gouraud')

# plt.ylabel('Frequency [Hz]')

# plt.xlabel('Time [sec]')
# plt.savefig(f'{report_out_path}/spec_{study_id}.png')


# S = np.abs(librosa.st)

# n = len(custom_waveform) # length of the signal
n =int(min(window_size, len(custom_waveform)))
# n = window_size
# print ('Building fft - librosa')
# # take the abs of the complex solution -> this is the aplitude
# S = np.abs(librosa.stft(custom_waveform, n_fft=active_nfft))
# # S[f][t]

# print (S)

print ('Building fft - np.nfft')
print (f'n : {n}')
Y = np.fft.fft(custom_waveform)/n
Y = Y[:n//2]
amplitudes =  abs(Y) 
max_power = np.max(amplitudes)

# print (f'max power : {max_power}')

# print (amplitudes)
# print (len(amplitudes))

# freq = np.fft.fftfreq(n, 1/sample_rate)
# print ('frequencies')
# print (freq)


k = np.arange(n)
T = n/sample_rate
frq = k/T # two sides frequency range
frq = frq[:len(frq)//2] # one side frequency range

xs = []
for i in range(0,len(amplitudes)):
    xs.append(i)
    
# print (xs)
# print (len(xs))




# frequencies = np.fft.fftfreq(active_nfft) * active_nfft * 1 / (t1 - t0)
# print (frequencies)

# S = librosa.amplitude_to_db(S**2,ref=np.max)
# print (S)
# S = S[:n//2]
# # Frequency components
# freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=active_nfft)
# print (freqs)

# amplitudes = 10*np.log10(amplitudes/n)
amplitudes=[convert_to_decibel(i) for i in amplitudes]

duration = len(custom_waveform)/sample_rate
# print (amplitudes)
plt.plot(frq,amplitudes,color='green',linewidth=0.1, markersize=0.5) # plotting the spectrum
plt.xlabel('f [Hz]')
plt.title(f'Power Spectrum (log10) ({duration}s)')
plt.ylabel('Power (dB)')
# plt.xlim(0, 300000)
# plt.ylim(-200,0)
# plt.xlim(f_min, f_max)
plt.savefig(f'{report_out_path}/dbpowerprofile_{study_id}.png')

# plt.savefig(f'{report_out_path}/dft_{study_id}_2000.png')
plt.close()
# exit()


# plt.plot(freqs,S) # plotting the spectrum
# plt.xlabel('Freq (Hz)')
# plt.ylabel('dB Power')
# plt.xlim(0, 300)
# plt.savefig(f'{report_out_path}/dft_{study_id}_300.png')
# plt.xlim(0, 20000)
# plt.savefig(f'{report_out_path}/dft_{study_id}_2000.png')
# plt.close()

duration = len(custom_waveform)/sample_rate
n = len(custom_waveform)
Y = np.fft.fft(custom_waveform)/n # dft and normalization
Y = Y[:n//2]

k = np.arange(n)
T = n/sample_rate
frq = k/T # two sides frequency range
frq = frq[:len(frq)//2] # one side frequency range

# print ('---')
# print (len(Y))
# Y = librosa.amplitude_to_db(np.abs(Y),ref=np.max)
# print (Y)
# plt.semilogy(frq,abs(Y**2)) # plotting the spectrum
plt.plot(frq,abs(Y),color='green',linewidth=0.1, markersize=0.5) 
plt.title(f'Power Spectrum ({duration}s)')
plt.xlabel('f (Hz)')
plt.ylabel('|P(freq)|')

plt.xlim(f_min, f_max)
plt.savefig(f'{report_out_path}/powerprofile_{study_id}.png')
plt.close()

# waveform
duration = len(custom_waveform)/sample_rate
time_vec = np.arange(0,duration,1/sample_rate) #time vector
plt.plot(time_vec,custom_waveform,color='green', linewidth=0.1, markersize=0.5)
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.title("Waveform")
plt.savefig(f'{report_out_path}/waveform_{study_id}.png')

#  python3 /home/vixen/rs/dev/marlin_hp/marlin_hp/report.py 2797069 20 300 298448815225760525793106 963118742699735308517278