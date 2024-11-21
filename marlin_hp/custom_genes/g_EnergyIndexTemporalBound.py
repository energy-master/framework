

"""
Gene : Frequency bounnds gene. Return 1 if True. True if f domain is in range of gene.


"""

version = 1.0
print (f"EnergyFrequencyBound [{version}]")

from marlin_brahma.genes.gene_root import *
import random, json, math
from datetime import timedelta


#{'min_f' : 130000, 'max_f': 150000}

class EnergyIndexTemporalBound(ConditionalRoot):
  def __init__(self,env=None,  gene_args = None):
    """[summary]

    :param env: [description], defaults to None
    :type env: [type], optional
    """
    
    #print (gene_args)
    super().__init__(condition='energy_index_temporal_bound', env=env)
    
    
    max_memory = gene_args['max_memory']
    min_index = gene_args['f_index_min']
    max_index = gene_args['f_index_max']
    min_threshold = gene_args['delta_energy_min']
    max_threshold = gene_args['delta_energy_max']
    
    self.memory = random.uniform(0 , max_memory) # ms
    self.frequency_index = math.floor(random.uniform(min_index , max_index))   
    # self.energy_threshold = random.uniform(0.01, 0.15)  
    self.energy_threshold = random.uniform(min_threshold,max_threshold)  
    

  def __str__(self):
    description = {}
    overview = super().__str__()
    data = {
        "decision type" : "EnergyIndexTemporalBound",
        "frequency index" : self.frequency_index,
        "energy_threshold" : self.energy_threshold,
        "memory" : self.memory
    }
    
    description['overview'] = overview
    description['data'] = data
    
    return ((description))
    


  def run(self, data = {}):
    import math
    avg_energy = 0
    
    # get f at timestamps
    derived_data = data['derived_model_data']
    iter_start_time = data['iter_end_time']
    stats = None
    
    geneInit = False
    
    # check init state
    sample_rate = data['sample_rate']
    current_data_index = data['data_index'] 
    current_data_delta_time = (current_data_index/sample_rate) * 1000 # ms
    
    self.Start()
    self.state = 0

    if current_data_delta_time > self.memory:
        geneInit = True
        
    if geneInit:
        # print ("init")
        self.Safe()
        stats_pivot = None
        bounds_data = derived_data.query_stats_freq_index(self.frequency_index, iter_start_time)
        stats_pivot = bounds_data.stats
        
        stats_ref = None
        memory_ref_time = iter_start_time - timedelta(milliseconds=self.memory)
        bounds_data = derived_data.query_stats_freq_index(self.frequency_index, memory_ref_time)
        stats_ref = bounds_data.stats
        
        delta_f = 0
        delta_f = abs(stats_ref['max_energy'] - stats_pivot['max_energy'])
    
        # print (stats_pivot)
        # print (stats_ref)
       
        # print (f'avg e : {avg_energy} {self.lower_frequency} - {self.upper_frequency}')
        # print (f'avg e : {avg_energy} {self.lower_frequency} - {self.upper_frequency}')
        if stats_pivot == None or stats_ref == None:
            print (f'Critical error in index time bounds DM.')
            exit()
            pass

        else:
            # print (avg_energy)
            # print (delta_f)
            file_out = False
            if file_out:
                outfile_name = f'{self.frequency_index}_{self.memory}__deltapower.txt'
                with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/{outfile_name}', 'a+') as f:
                    f.write(f'{iter_start_time} {avg_energy}\n')
                self.Safe()

            if delta_f > self.energy_threshold:
                # print (f'trigger {delta_f} > {self.energy_threshold}')
                return 1

            return 0
    # print ("not init")
    return 0
  
  def mutate(self, data = {}):
    
    # print (f'gene [energy_frequency_bound] mutating')
    # print (self.energy_threshold)
    # factor = random.uniform(-1,1)
    factor = 1
    creep_rate = data['creep_rate']
    
    # #min_f
    # self.lower_frequency = self.lower_frequency + (creep_rate*random.uniform(1,factor))
    # #max_f
    # self.upper_frequency = self.upper_frequency + (creep_rate*random.uniform(1,factor))
      
    # self.lower_frequency = min(self.lower_frequency,self.upper_frequency)
    # self.upper_frequency = max(self.lower_frequency,self.upper_frequency)
    
    self.energy_threshold = self.energy_threshold + (creep_rate*factor)
    # print (f'mutate threshold  : {self.energy_threshold}')
    
      


    





