
## ---------------------------------------------------------------------------  #
# ===================================================                           #
# | Harbour Popoise Detection Genetic Algorithm     |                           #
# | On demand spectrogram                           |                           #
# ===================================================                           #
#                                                                               #
#                                                                               #
#                                                                               #
#  c. Rahul Tandon, 2024, RSA 2024                                              #
#                                                                               #
## ---------------------------------------------------------------------------- #

import sys
import os

os.environ['LIBROSA_CACHE_DIR'] = '/home/vixen/html/rs/ident_app/ident/brahma/out/spec/'
import librosa
import urllib.request

sys.path.append('/home/vixen/rs/dev/marlin_data/marlin_data')
from marlin_data import *
from utils import *
import scipy.io.wavfile as wavfile
# Init data adapter (marlin adapter)
data_adapter = None
data_adapter = MarlinData(load_args={'limit' : 10})


# def build_spec(data,  id, bot_id):
#     print ("building spec")
#     y = data.frequency_ts_np * 40
#     n_fft = 8192
#     sample_rate = data.meta_data['sample_rate']
   
#     print ("build")
#     plt.specgram(y,NFFT=n_fft, Fs=sample_rate, scale="dB",mode="magnitude",cmap="ocean")
#     print ("done")
   
#     plt.ylabel('Frequency [Hz]')
#     plt.xlabel('Time [sec]')
   
    
#     filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_spec.png'
#     plt.savefig(filepath)
    
   
    


def download_data(location, sim_ids):
    
    data_adapter.download_simulation_snapshots(load_args={ 'location':location, 'ss_ids' : sim_ids})
   



#------------------- Entry RUN ----------------------

command = False
sim_ids = []
location = []
if (len(sys.argv) > 1):
    
    # required
    snapshot_id     =   sys.argv[1]
    location_id     =   sys.argv[2]
    identifier      =   sys.argv[3]
    # optional
    try:
        n_fft                       =   sys.argv[4]
    except:
        n_fft                       = None
    try: 
        f_min                       =   sys.argv[5]
    except:
        f_min                       = 0
    try:
        f_max                       =   sys.argv[6]
    except:
        f_max                       = 0
    try:
        custom                      =   sys.argv[7]
    except:
        custom                      = 0
    try:
        custom_filepath             =   sys.argv[8]
    except:
        custom_filepath             = ""
    try:
        custom_sr                   =   sys.argv[9]
    except:
        custom_sr                   = 96000
        
    
    command = True
print (f'nfft {n_fft}')
print (f'fn {custom_filepath}')
print (f'custom {custom}')
if custom == "0":
    print ("not custom")
    #prepare download parms
    sim_ids.append(snapshot_id)
    print (sim_ids)
    location.append(location_id)

    # download data
    download_data(location=location, sim_ids=sim_ids)

    # build streamer
    data_feed = None
    data_feed = MarlinDataStreamer()
    data_feed.init_data(data_adapter.simulation_data, data_adapter.simulation_index)


    for snapshot in data_feed:
        #print (snapshot.frequency_ts_np)
        build_spec(snapshot, identifier,  "debug", n_fft=n_fft, f_min=f_min, f_max=f_max, custom=0, sr=96000)

if custom == "1":
    print ("custom")
    # data, sr = librosa.load(custom_filepath)
    
    urllib.request.urlretrieve(custom_filepath, f'/home/vixen/html/rs/ident_app/ident/brahma/out/spec/{identifier}_sample.wav')
    #data, sr = librosa.load(f'/home/vixen/html/rs/ident_app/ident/brahma/out/spec/{identifier}_sample.wav')
    sr, data = wavfile.read(f'/home/vixen/html/rs/ident_app/ident/brahma/out/spec/{identifier}_sample.wav')
    build_spec(data,  identifier,  "debug", n_fft=n_fft, f_min=f_min, f_max=f_max, custom=1, sr=sr, identifier=identifier)
   