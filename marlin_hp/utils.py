import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import random
import numpy as np
from scipy.interpolate import make_interp_spline

from scipy import signal
from scipy.fft import fftshift
from datetime import datetime
"""
    Game level utils
"""


def get_bin_f(librosa_f_bins, freq_lower, freq_end):
    cnt = 0
    start_diff = 100000
    end_diff = 10000
    for value in librosa_f_bins:
        
        # print (f'{value}')
        if (abs(value-freq_lower) < start_diff):
            print (abs(value-freq_lower))
            start_diff = abs(value-freq_lower)
            index_start = cnt
            print (f'{index_start}')
        if (abs(value-freq_end) < end_diff):
            index_end = cnt
            end_diff = abs(value-freq_end)
            print (abs(value-freq_lower))
            print (f'{index_end}')
        cnt+=1
        
    print (f'{index_start} | {librosa_f_bins[index_start]} => {index_end} | {librosa_f_bins[index_end]}')
    return index_start, index_end
    
def plot_hist(frequency_activity, filename):
    
    plt.hist(frequency_activity, range = (100000, 200000), bins = 100)
    plt.savefig(filename)
    plt.clf()


def build_spec_upload(data, game_id,  hits, decisions,peak,avg,times,pc_above_e, f=[] ):
    
    
    if peak != []:
        peak.append(0.0)
        avg.append(0.0)
        pc_above_e.append(0.0)
    
   
    sample_rate = data.meta_data['sample_rate']
    
    n_fft = 8192
    
    y = data.frequency_ts_np * 40
    
    fig, ax1 = plt.subplots(figsize=(8, 8))
    plt.specgram(y,NFFT=n_fft, Fs=sample_rate, scale="dB",mode="magnitude",cmap="ocean")
    
    filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/spec/{game_id}.png'
    plot_time = []
    
    for idx in decisions:
        
        _t = datetime.strptime(idx['time'],"%Y-%m-%dT%H:%M:%S.%fZ")
        
        _s = _t.strftime('%-S.%f')
        print (_s)
        plt.plot(float(_s), 100000, 'go')

    
    for time in times:
        _t = datetime.strptime(times[time],"%Y-%m-%dT%H:%M:%S.%fZ")
        _s = _t.strftime('%-S.%f')
        plot_time.append(float(_s))
    
    # for i, val in enumerate(peak):
    #     if val<0.7:
    #         peak[i] = 0
    
    avg_plot_50 = [((0.5 * 50000) + 200000) for i in avg]
    pc_above_e_plot_50 = [(((50/100) * 50000) + 250000) for i in pc_above_e]
    energy_50_plot =  [(((50/100) * 20000)) for i in pc_above_e]
    
    peak_plot = [i * 20000 for i in peak]
    avg_plot = [((i * 50000) + 200000) for i in avg]
    pc_above_e_plot = [(((i/100) * 50000) + 250000) for i in pc_above_e]
    
    
    
    color = (0.2, # redness
         0.4, # greenness
         0.2, # blueness
         1.0 # transparency
        ) 
    pk_color = (1.0, # redness
         0.2, # greenness
         0.4, # blueness
         1.0 # transparency
        ) 
    # print (avg)
    # print (avg_plot)
    plt.plot(plot_time,avg_plot,color=pk_color)
    plt.plot(plot_time,peak_plot,color=pk_color)
    plt.plot(plot_time,pc_above_e_plot,color=pk_color)
    plt.plot(plot_time,avg_plot_50,color='w')
    plt.plot(plot_time,pc_above_e_plot_50,color='w')
    plt.plot(plot_time,energy_50_plot,color='w')
    
    
    plt.colorbar()
    

    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (s)')
    plt.savefig(filepath)
    plt.clf()
    
def build_spec(data,  id, bot_id, n_fft = None, f_min = 0, f_max = 0, custom=0, sr=96000, identifier=0, times=[], energies=[], hits = [], activation_level=0.2):
    print ("building spec")
    
    if custom == 0:
    
    
        e_profile = np.array(energies)
        t_profile = np.array(times)
    
        y = data.frequency_ts_np * 40
        if n_fft == None:
            n_fft = 8192
        else:
            n_fft = int(n_fft)
        
        sample_rate = data.meta_data['sample_rate']
        print (activation_level)
        print ("build")
        plt.specgram(y,NFFT=n_fft, Fs=sample_rate, scale="dB",mode="magnitude",cmap="ocean")
                
        # X_Y_Spline = make_interp_spline(f_profile, e_profile)
        # # Returns evenly spaced numbers
        # # over a specified interval.
        # X_ = np.linspace(f_profile.min(), f_profile.max(), 500)
        # Y_ = X_Y_Spline(X_)

        # plt.plot( t_profile,e_profile , '-')
        # plt.plot( X_,Y_ , '-',color='green' )
        
        for idx, e in enumerate(energies):
            if e > float(activation_level):
                
                plt.plot(times[idx], 100000, 'go')
        
        for idx, e in enumerate(hits):
            if e == 1:
                plt.plot(times[idx], 150000, 'bv')
                
        plt.colorbar()
        print ("done")
    
        plt.ylabel('Frequency (H)')
        plt.xlabel('Time (s)')
        
        if f_max != 0:
            plt.ylim([int(f_min), int(f_max)])

        if bot_id != "debug":
            snapshot_id =  data.meta_data['snapshot_id']
            filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_spec.png'
        
        else:
            snapshot_id =  data.meta_data['snapshot_id']
            filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/spec/{id}.png'
        
        
        
        
        plt.savefig(filepath)
    
    
    
    
    if custom == 1:
    
        y = data * 40
        if n_fft == None:
            n_fft = 8192
        else:
            n_fft = int(n_fft)
        
        sample_rate = sr
        print ("build")
        plt.specgram(y,NFFT=n_fft, Fs=sample_rate, scale="dB",mode="magnitude",cmap="ocean")
        plt.colorbar()
        print ("done")
    
        plt.ylabel('Frequency (H)')
        plt.xlabel('Time (s)')
        
        if f_max != 0:
            plt.ylim([int(f_min), int(f_max)])

        if bot_id != "debug":
            snapshot_id =  data.meta_data['snapshot_id']
            filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_spec.png'
        
        else:
            
            filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/spec/{identifier}.png'
        
        plt.savefig(filepath)
    
  
    
    

def build_waveform(data, id, bot_id):
    v = data.frequency_ts_np
    snapshot_id =  data.meta_data['snapshot_id']
    filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_waveform.png'
    sampling_rate = data.meta_data['sample_rate']
    
    fig, ax = plt.subplots(figsize=(10, 5))
    img = librosa.display.waveshow(v, sr=sampling_rate)
    # plt.colorbar()
    fig.savefig(f'{filepath}')
    plt.close(fig)
  
def build_f_profile(data, id, bot_id):
    v = data.frequency_ts_np
    print ('data')
    print (v)
    snapshot_id =  data.meta_data['snapshot_id']
    
    sampling_rate = data.meta_data['sample_rate']
    n_fft = 16384
    filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_f_profile1.png'
    ft = np.abs(librosa.stft(data.frequency_ts_np[:n_fft], hop_length = n_fft+1))
    librosa_f_bins = librosa.core.fft_frequencies(n_fft=n_fft, sr=sampling_rate)
   
   
    
    
    # index_start  = min(range(len(librosa_f_bins)), key=lambda i: abs(librosa_f_bins[i]-freq_lower))
    # index_end  = min(range(len(librosa_f_bins)), key=lambda i: abs(librosa_f_bins[i]-freq_end))
    
    #--- plt 1
    
    index_start = 0
    index_end = 0
    freq_lower = 30
    freq_end = 1000
    index_start, index_end = get_bin_f(librosa_f_bins, freq_lower, freq_end)
    
    freqs = []
    ft_p = []
    # ft = ft[index_start:index_end]
    for i in range(index_start,index_end):
        freqs.append(librosa_f_bins[i])
        ft_p.append(ft[i])
    
    plt.plot(freqs, ft_p);
    
    plt.title(f'Power Spectrum {freq_lower}:{freq_end}');
    # plt.xlim(20,1000)
    plt.xlabel('Frequency (Hz)');
    plt.ylabel('Amplitude (db)');
    plt.savefig(filepath)
    plt.clf()
    
    
    #--- plt 2
    
    index_start = 0
    index_end = 0
    freq_lower = 0
    freq_end = 2000
    index_start, index_end = get_bin_f(librosa_f_bins, freq_lower, freq_end)
    ft_p = []
    freqs = []
    # ft = ft[index_start:index_end]
    for i in range(index_start,index_end):
        freqs.append(librosa_f_bins[i])
        ft_p.append(ft[i])
    
    filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_f_profile2.png'
    print ('data length')
    print (len(ft))
    print ('f length')
    print (len(freqs))
    print (f'{index_start} => {index_end}')
    
    plt.plot(freqs,ft_p);
    plt.title(f'Power Spectrum {freq_lower}:{freq_end}');
    plt.xlabel('Frequency Bin');
    plt.ylabel('Amplitude');
    plt.savefig(filepath)
    plt.clf()
    
    #--- plt 3
    
    index_start = 0
    index_end = 0
    freq_lower = 0
    freq_end = 400
    index_start, index_end = get_bin_f(librosa_f_bins, freq_lower, freq_end)
    
    freqs = []
    # ft = ft[index_start:index_end]
    
    
    ft_p = []
    for i in range(index_start,index_end):
        freqs.append(librosa_f_bins[i])
        ft_p.append(ft[i])
    
    filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_f_profile3.png'
    print (len(ft))
    plt.plot(freqs, ft_p);
    plt.title(f'Power Spectrum {freq_lower}:{freq_end}');
    plt.xlabel('Frequency Bin (Hz)');
    plt.ylabel('Amplitude (db)');
    plt.savefig(filepath)
    plt.clf()
    
     #--- plt 4
    
    # index_start = 0
    # index_end = 0
    # freq_lower = 0
    # freq_end = librosa_f_bins[len(librosa_f_bins)-3]
    # freq_end = 20000
    # index_start, index_end = get_bin_f(librosa_f_bins, freq_lower, freq_end)
    
    # ft_p = []
    # freqs = []
    
    # for i in range(index_start,index_end):
    #     freqs.append(librosa_f_bins[i])
    #     ft_p.append(ft[i])
    # filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_f_profile3.png'
    # print (len(ft))
    # plt.bar(freqs, ft_p);
    # plt.title(f'Power Spectrum {freq_lower}:{freq_end}');
    # plt.xlabel('Frequency Bin (Hz)');
    # plt.ylabel('Amplitude (db)');
    # plt.savefig(filepath)
    # plt.clf()
    
  