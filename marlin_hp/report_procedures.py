import math
from scipy.stats import norm, kurtosis, entropy
import matplotlib.pyplot as plt
import numpy as np
import librosa

# main_entropy_profile = {}

def grab_entropy_across_f_bins(iter_idx, derived_data, s_r):
    # print (derived_data.delta_t)
    time_lookup_idx = math.floor((iter_idx/s_r)/derived_data.delta_t)
    print (time_lookup_idx)
    print(derived_data.delta_t)
    #print (derived_data.spectral_entropy_across_freq[time_lookup_idx])
    return (derived_data.spectral_entropy_across_freq[time_lookup_idx])


def calculate_kurtosis(vector):
    k = 0
    
    k = kurtosis(vector)
    
    return k


kurtosis_tracker = {}
def grab_kurtosis_at_f_t(f_index, derived_data, time, delta_f):
    
    entropy_track = []
    fft_track = {}
    active_group = 0
    active_upper_bound = delta_f
    psd_tracker = {}
    entropy_tracker = {}
    
    while active_upper_bound < 600:
        for k,v in derived_data.fast_index_energy_stats.items():
            
            stats = derived_data.query_stats_freq_index(k, time)
            #print (stats)
            
            lower_f = (stats.frequency_bounds[0])
            upper_f = (stats.frequency_bounds[1])
            if upper_f < active_upper_bound:
                if active_group not in fft_track:
                    fft_track[active_group] = []
                
                for val in stats.energy_profile:
                    fft_track[active_group].append(val)
                    # print (len(fft_track[active_group]))
                    
                
        active_upper_bound += delta_f
        active_group += 1
    
    #entropy = float(sum(entropy_track)/len(entropy_track))
    total_psd = 0
    
    for k,v in fft_track.items():
        kurt = calculate_kurtosis(v)
        if k not in kurtosis_tracker:
            kurtosis_tracker[k] = []
        kurtosis_tracker[k].append(kurt)
        
  
        
    
    
    
    
    
    entropy = 0
    return entropy
        
def build_f_profile(time, derived_data, frequency_energy_profile):
    no_stat_cnt = 0
    for k,v in derived_data.fast_index_energy_stats.items():
        
        stats = derived_data.query_stats_freq_index(k, time)
        # print (stats)
        
        
        if 'max_energy' in stats.stats:
            if k in frequency_energy_profile:
                frequency_energy_profile[k].append(stats.stats['max_energy'])
            else:
                frequency_energy_profile[k] = []
                frequency_energy_profile[k].append(stats.stats['max_energy'])
                
            
        else:
            pass
            
            # exit()
    


def build_f_profile_vector(time_s, time_e, derived_data, frequency_energy_profile, f_path):
    no_stat_cnt = 0
    current_frequency_energy_profile = {}
    max_e = 0
    for k,v in derived_data.fast_index_energy_stats.items():
        
        stats_v = derived_data.query_stats_vector_freq_index(k, time_s, time_e)
        energy = 0
        n_d = len(stats_v)
        print (f'number of domains in vector : {n_d}')
        for domain in stats_v:
            # print (domain.stats)
            if 'max_energy' in domain.stats:
                
                energy = domain.stats['max_energy']   
                max_e = max(max_e, energy)
                if k in frequency_energy_profile:
                    frequency_energy_profile[k].append(energy)
                else:
                    frequency_energy_profile[k] = []
                    frequency_energy_profile[k].append(energy)
                
                if k in current_frequency_energy_profile:
                    current_frequency_energy_profile[k].append(energy)
                else:
                    current_frequency_energy_profile[k] = []
                    current_frequency_energy_profile[k].append(energy)
        
        # print (f'max e : {max_e}')            
        # for domain in stats_v:
        #     print (domain.stats)
        #     if 'mean_energy' in domain.stats:
        #         energy += domain.stats['mean_energy']    
        #         if k in frequency_energy_profile:
        #             frequency_energy_profile[k].append(energy)
        #         else:
        #             frequency_energy_profile[k] = []
        #             frequency_energy_profile[k].append(energy)
                
        #         if k in current_frequency_energy_profile:
        #             current_frequency_energy_profile[k].append(energy)
        #         else:
        #             current_frequency_energy_profile[k] = []
        #             current_frequency_energy_profile[k].append(energy)
        
        # for domain in stats_v:
        #     print (domain.stats)
        #     if 'mean_energy' in domain.stats:
        #         energy += domain.stats['mean_energy']    
        #         if k in frequency_energy_profile:
        #             frequency_energy_profile[k].append(energy)
        #         else:
        #             frequency_energy_profile[k] = []
        #             frequency_energy_profile[k].append(energy)
                
        #         if k in current_frequency_energy_profile:
        #             current_frequency_energy_profile[k].append(energy)
        #         else:
        #             current_frequency_energy_profile[k] = []
        #             current_frequency_energy_profile[k].append(energy)
    
        # print (frequency_energy_profile[0])
        # exit()
    
    index_vals = []
    energy_vals = []
    for freq, energy_vector in current_frequency_energy_profile.items():
        index_vals.append(freq)
        energy_vals.append(float(sum(energy_vector)/ len(energy_vector)))
    
    # print(len(index_vals))  
    # print(len(energy_vals))  
    plt.bar(index_vals,energy_vals)
    plt.savefig(f_path)
    plt.clf()

def calculate_study_frequency_profile(study_frequency_profile):
    frequency_hist = {}
    for f_index, value in study_frequency_profile.items():
        # print (study_frequency_profile[f_index])
        # exit()
        sum_energy = sum(value)
        # print (sum_energy)
        avg_energy = float(sum_energy/len(value))
        # print (avg_energy)
        frequency_hist[f_index] = avg_energy
        # print (frequency_hist[f_index])
    
    
    return frequency_hist

def calculate_entropy_stats(entropy_list):
    # print (entropy_list)
    pass
    
# def build_entropy_stats(time, derived_data, frequency_energy_profile):
def convert_to_decibel(arr):
    ref = 1
    if arr!=0:
        return 20 * np.log10(abs(arr) / ref)
        
    else:
        print ('d')
        return -60