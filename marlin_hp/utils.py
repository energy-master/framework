import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import random
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
    

def build_spec(data,  id, bot_id):
    y = data.frequency_ts_np * 40
    n_fft = 8192
    D = librosa.stft(y, n_fft=n_fft,hop_length = n_fft // 2)  # STFT of y
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max,amin=20)
    # S_db = np.abs(D)
    sample_rate = data.meta_data['sample_rate']
    print (S_db[len(S_db)-1])
    snapshot_id =  data.meta_data['snapshot_id']
    filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_spec.png'
   
   
    
    plt.figure(figsize=(12, 5))
    librosa.display.specshow(S_db, sr=sample_rate, y_axis='linear', x_axis='time')
    # tick_frames = librosa.time_to_frames(np.arange(1, 6))
    # plt.xlim([0, tick_frames[-1]])

    freqs = librosa.fft_frequencies()
    print (freqs)
    max_bin = np.flatnonzero(freqs >= 2000)[0]
    min_bin = np.flatnonzero(freqs <= 100000)[0]
    
    plt.ylim([0, 145000])
    
    # librosa.display.time_ticks(tick_frames, librosa.frames_to_time(tick_frames))
    plt.xlabel('Time')
    plt.ylabel('Hz')
    plt.savefig(filepath)
    
    
    

def build_waveform(data, id, bot_id):
    v = data.frequency_ts_np
    snapshot_id =  data.meta_data['snapshot_id']
    filepath = f'/home/vixen/html/rs/ident_app/ident/brahma/out/{snapshot_id}_{bot_id}_main_waveform.png'
    sampling_rate = data.meta_data['sample_rate']
    
    fig, ax = plt.subplots(figsize=(10, 5))
    img = librosa.display.waveshow(v, sr=sampling_rate)
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
    
  