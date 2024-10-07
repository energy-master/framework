import math


# main_entropy_profile = {}

def grab_entropy_across_f_bins(iter_idx, derived_data, s_r):
    # print (derived_data.delta_t)
    time_lookup_idx = math.floor((iter_idx/s_r)/derived_data.delta_t)
    # print (time_lookup_idx)
    #print (derived_data.spectral_entropy_across_freq[time_lookup_idx])
    return (derived_data.spectral_entropy_across_freq[time_lookup_idx])

def grab_entropy_at_f_t(f_index, derived_data, time, min_f, max_f):
    
    entropy_track = []
    for k,v in derived_data.fast_index_energy_stats.items():
        
        stats = derived_data.query_stats_freq_index(k, time)
        lower_f = (stats.frequency_bounds[0])
        upper_f = (stats.frequency_bounds[1])
        if lower_f > min_f and lower_f < max_f:
            entropy_track.append(stats.stats['entropy'])
            
    entropy = float(sum(entropy_track)/len(entropy_track))
    
    return entropy
        
def build_f_profile(time, derived_data, frequency_energy_profile):
    
    for k,v in derived_data.fast_index_energy_stats.items():
        
        stats = derived_data.query_stats_freq_index(k, time)
        if k in frequency_energy_profile:
            frequency_energy_profile[k].append(stats.stats['max_energy'])
        else:
            frequency_energy_profile[k] = []
            frequency_energy_profile[k].append(stats.stats['max_energy'])
   
    

def calculate_study_frequency_profile(study_frequency_profile):
    frequency_hist = {}
    for f_index, value in study_frequency_profile.items():
        sum_energy = sum(value)
        # print (sum_energy)
        avg_energy = float(sum_energy/len(value))
        # print (avg_energy)
        frequency_hist[f_index] = avg_energy
        
    return frequency_hist
    
    
    