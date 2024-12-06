

import math, statistics
from utils import *
# --------------------------------------------------------------
# --- Layer 3 Class ---                                          |
# --------------------------------------------------------------


    
class Layer_Three(object):
    
    def __init__(self, activation_level, threshold_above_activation, derived_data = None, similarity_threshold=0.8, run_id="", target=""):
        
        self.target = target
        
        self.activation_level = activation_level
        self.threshold_above_e = threshold_above_activation
        self.decisions = []
        self.peak_energies = []
        self.avg_energies = []
        self.run_id = run_id
        #?
        self.pc_above_tracker = []
        self.thresh_80_tracker = []
        self.thresh_50_tracker = []
        self.ratio_active = []
        
        
        # structure methodology
        self.similarity_threshold = similarity_threshold
        self.structure_likelyhood = []
        self.derived_data = derived_data
        if self.target == "harbour_porpoise":
            self.structure_match = harbour_porpoise_structure(likelyhood=0.8,  derived_data = derived_data)
        if self.target == "sonar":
            self.structure_match = sonar_structure(likelyhood=0.8,  derived_data = derived_data)
    
        
    def get_frequency(self, idx):
        return self.derived_data.min_freq + (idx *  (self.derived_data.index_delta_f))
    
    def record_decision(self, frame_number, features, all_features = None):
        frequency_activity = []
        for feature in features:
            # print (feature.dNA[0].genome)
            for k,v in feature.dNA.items():
                for kg,vg in v.genome.items():
                    for kgg, vgg in vg.genome.items():
                        # if 'frequency_index' in vgg:
                        frequency_activity.append(self.get_frequency(vgg.frequency_index))
        
        filename = f'/home/vixen/html/rs/ident_app/ident/brahma/out/f_d_{self.run_id}_{frame_number}.png'
        plot_hist(frequency_activity, filename)
        
        # all features
        frequency_activity = []
        for feature in all_features:
            # print (feature.dNA[0].genome)
            for k,v in feature.dNA.items():
                for kg,vg in v.genome.items():
                    for kgg, vgg in vg.genome.items():
                        # if 'frequency_index' in vgg:
                        frequency_activity.append(self.get_frequency(vgg.frequency_index))
        
        filename = f'/home/vixen/html/rs/ident_app/ident/brahma/out/f_d_{self.run_id}_{frame_number}_all.png'
        plot_hist(frequency_activity, filename)
        
    
    def run_layer(self,energy_data, time_data,active_features=None, all_features = None):
        # print (time_data)
     
        number_frames = len(time_data)
        print (f'Number frames : {number_frames}')
        print (f'Number of active_features : {len(active_features)}')
        print (f'Number of all features : {len(all_features)}')
        freq = []
        
        for frame_count in range(0,number_frames-1):
            expression_list = []
            peak = False
            sum_above_a = 0
            number_features = 0
            max_energy = 0
            frame_decision = False
            # if frame_count in active_features:
            #     print (f'number of f in frame : {len(active_features[frame_count])} | {frame_count}')
            for feature, value in energy_data.items():
                
                feature_expression = value[frame_count]
                # print (feature_expression,self.activation_level )
                # if float(feature_expression) > float(self.activation_level):
                #     # print ('above')
                max_energy = max(max_energy, feature_expression)
                # print (f'ex: {feature_expression}')
                number_features += 1
                if float(feature_expression) > float(self.activation_level):
                    sum_above_a += 1
                    
                expression_list.append(feature_expression)
                if float(feature_expression) > float(self.activation_level):
                    peak = True
            

            
            
            average_energy = statistics.mean(expression_list)
            # print (f'average_energy')
            # print (f'average : {average_energy} frame : {frame_count}')
            # score_80 = statistics.scoreatpercentile(expression_list, 80) 
            score_above = float(sum_above_a/number_features) * 100
            
            # print (f' score a {score_above}')
            self.avg_energies.append(average_energy)
            self.peak_energies.append(max_energy)
            self.pc_above_tracker.append(score_above)
            _r = 0.0
            if frame_count in active_features:
                
                _r = float(len(active_features[frame_count])/len(all_features))
                
                self.ratio_active.append(float(_r))
                
            else:
                self.ratio_active.append(0.0)
            
            # if float(average_energy) > float(self.activation_level):
            #     self.decisions.append({'time': time_data[frame_count], 'decision': 'ident', 'reason' :'avg_energy'})
            
            # if float(score_above) > float(self.threshold_above_e):
            #     self.decisions.append({'time': time_data[frame_count], 'decision': 'ident',  'reason' :'pc_above_ae'})
            
            
            similarity = 0.0
            freq = []
            
                
            print (_r, self.threshold_above_e)
            # if float(score_above) < float(50):
            if frame_count in active_features:
                if float(_r) > float(self.threshold_above_e):
                    similarity = 1.0
                    # print (float(self.threshold_above_e))
                    # print (active_features)
                    # if frame_count in active_features:
                    # similarity = self.structure_match.match(features = active_features[frame_count])
                            
            self.structure_likelyhood = similarity
            # similarity = 0.0
            if similarity > float(self.similarity_threshold):
                print (f'looking at frame {frame_count} ')
                self.decisions.append({'time': time_data[frame_count], 'decision': 'ident',  'reason' :'structure_similarity', 'frame' : frame_count, 'active_freq' : f'https://vixen.hopto.org/rs/ident_app/ident/brahma/out/f_d_{self.run_id}_{frame_count}.png' , 'all_freq' : f'https://vixen.hopto.org/rs/ident_app/ident/brahma/out/f_d_{self.run_id}_{frame_count}_all.png'})
                frame_decision = True
            
            if frame_decision:
                self.record_decision(frame_number=frame_count, features = active_features[frame_count], all_features=all_features)

                        
        # print (self.ratio_active)
        
        number_decisions = len(self.decisions)
        print (f' {number_decisions} made from {number_frames} frames.')
        print (self.decisions)
        
        return freq

class harbour_porpoise_structure(object):
    
    def __init__(self, likelyhood = 0.0, derived_data= None):
        self.likelyhood = likelyhood
        self.derived_data = derived_data
    
    def get_frequency(self, idx):
        return self.derived_data.min_freq + (idx *  (self.derived_data.index_delta_f))
    
    def match(self, features = [] ):
        
        
        #*** frequency structure ***
        
        frequency_activity = []
        print (f'number features to build structure : {len(features)}')
        # if (len(features) < 4):
        #     return 0
        
        likely_match = 0.0
        for feature in features:
            # print (feature.dNA[0].genome)
            for k,v in feature.dNA.items():
                for kg,vg in v.genome.items():
                    for kgg, vgg in vg.genome.items():
                        # if 'frequency_index' in vgg:
                        _f = self.get_frequency(vgg.frequency_index)
                        frequency_activity.append(_f)
                        unique_f = len(set(frequency_activity))
                        
                        # if vgg.frequency_index < 120000:
                        #     return 0
                        # else:
                        #     pass
                        
        
        # frequenct profile
        
        # q = [round(q, 1) for q in statistics.quantiles(frequency_activity, n=20)]
        # print (self.derived_data.min_freq, self.derived_data.max_freq)
        # print (q)
        # print (frequency_activity)
        
        if len(frequency_activity) >= 0:
            # avg_value = statistics.mean(q[math.floor((20/4)*3):len(q)])
            avg_value = 0.0
            if len(frequency_activity) > 3:
                # return 1.0
                avg_value = statistics.mean(frequency_activity)
            else:
                avg_value = frequency_activity[0]    
            
            # print (avg_value)
            # if max(avg_value,120000) >= 135000:
            # 120 - 140 kHz
            # print (avg_value)
            if avg_value > 125000:
                
                likely_match = 1.0
                return likely_match
        
        return (likely_match)


class sonar_structure(object):
    
    def __init__(self, likelyhood = 0.0, derived_data= None):
        self.likelyhood = likelyhood
        self.derived_data = derived_data
    
    def get_frequency(self, idx):
        return self.derived_data.min_freq + (idx *  (self.derived_data.index_delta_f))
    
    def match(self, features = [] ):
        
        
        #*** frequency structure ***
        
        frequency_activity = []
        print (f'number features to build structure : {len(features)}')
        # if (len(features) < 4):
        #     return 0
        
        likely_match = 0.0
        for feature in features:
            # print (feature.dNA[0].genome)
            for k,v in feature.dNA.items():
                for kg,vg in v.genome.items():
                    for kgg, vgg in vg.genome.items():
                        # if 'frequency_index' in vgg:
                        _f = self.get_frequency(vgg.frequency_index)
                        frequency_activity.append(_f)
                        unique_f = len(set(frequency_activity))
                        
                        # if vgg.frequency_index < 120000:
                        #     return 0
                        # else:
                        #     pass
                        
        
        # frequenct profile
        
        # q = [round(q, 1) for q in statistics.quantiles(frequency_activity, n=20)]
        # print (self.derived_data.min_freq, self.derived_data.max_freq)
        # print (q)
        # print (frequency_activity)
        
        if len(frequency_activity) >= 0:
            # avg_value = statistics.mean(q[math.floor((20/4)*3):len(q)])
            avg_value = 0.0
            if len(frequency_activity) > 3:
                # return 1.0
                avg_value = statistics.mean(frequency_activity)
            else:
                avg_value = frequency_activity[0]    
            
            print (avg_value)
            # if max(avg_value,120000) >= 135000:
            if avg_value < 130000:
                
                likely_match = 1.0
                return likely_match
        
        return (likely_match)