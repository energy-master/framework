

"""
Gene : Frequency bounnds gene. Return 1 if True. True if f domain is in range of gene.


"""

version = 1.0
print (f"EnergyFrequencyBound [{version}]")

from marlin_brahma.genes.gene_root import *
import random, json, math
from datetime import timedelta


#{'min_f' : 130000, 'max_f': 150000}

class IndexKurtosis(ConditionalRoot):
  def __init__(self,env=None,  gene_args = None):
    """[summary]

    :param env: [description], defaults to None
    :type env: [type], optional
    """
    
    #print (gene_args)
    super().__init__(condition='energy_index_temporal_bound', env=env)
    
    
    
    min_index = gene_args['f_index_min']
    max_index = gene_args['f_index_max']
    min_threshold = gene_args['kurtosis_min']
    max_threshold = gene_args['kurtosis_max']
    self.max_kurtosis = gene_args['kurtosis_max']
    self.min_kurtosis = gene_args['kurtosis_min']
    # min_threshold = gene_args['delta_energy_min']
    # max_threshold = gene_args['delta_energy_max']
    
    self.max_index = max_index
    
    self.frequency_index = math.floor(random.uniform(min_index , max_index))   
    # self.energy_threshold = random.uniform(0.01, 0.15)  
    self.kurtosis_threshold = random.uniform(min_threshold,max_threshold)  
    self.memory = 1

  def __str__(self):
    description = {}
    overview = super().__str__()
    data = {
        "decision type" : "IndexKurtosisSinglePoint",
        "frequency index" : self.frequency_index,
        "kurtosis_threshold" : self.kurtosis_threshold,
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
        
        self.Safe()
        stats_pivot = None
        bounds_data = derived_data.query_stats_freq_index(self.frequency_index, iter_start_time)
        if bounds_data == None:
          return 0
        stats_pivot = bounds_data.stats
        #print(stats_pivot)
        
       
        # delta_f = 0
        # delta_f = abs(stats_ref['max_energy'] - stats_pivot['max_energy'])
        # delta_f_pc = (delta_f / max(stats_ref['max_energy'],stats_pivot['max_energy']))  * 100
        kurtosis_value = stats_pivot["kurtosis"]
        # print (kurtosis_value)
        # print (f'avg e : {avg_energy} {self.lower_frequency} - {self.upper_frequency}')
        # print (f'avg e : {avg_energy} {self.lower_frequency} - {self.upper_frequency}')
        if stats_pivot == None:
            print (f'Critical error in index time bounds DM.')
            exit()
            pass

        else:
           
            # print (avg_energy)
            file_out = False
            if file_out:
                outfile_name = f'{self.frequency_index}_{self.memory}__deltapower.txt'
                with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/{outfile_name}', 'a+') as f:
                    f.write(f'{iter_start_time} {avg_energy}\n')
                self.Safe()

            if kurtosis_value > self.kurtosis_threshold:
                #print (f'trigger {kurtosis_value} > {self.kurtosis_threshold}')
                return 1

            return 0
    # print ("not init")
    return 0
  
  def mutate(self, data = {}):
    
    # print (f'gene [energy_frequency_bound] mutating')
    # print (self.energy_threshold)
    factor = random.uniform(-1,1)
    #factor = 1
    creep_rate = data['creep_rate']
    
    # #min_f
    # self.lower_frequency = self.lower_frequency + (creep_rate*random.uniform(1,factor))
    # #max_f
    # self.upper_frequency = self.upper_frequency + (creep_rate*random.uniform(1,factor))
      
    # self.lower_frequency = min(self.lower_frequency,self.upper_frequency)
    # self.upper_frequency = max(self.lower_frequency,self.upper_frequency)
    # print (self.kurtosis_threshold)
    m_rate = (abs(float(self.max_kurtosis) - float(self.min_kurtosis))) / float(random.uniform(0,creep_rate))
    self.kurtosis_threshold = self.kurtosis_threshold + (m_rate*factor)
    # print (self.kurtosis_threshold)
    self.frequency_index = math.floor(random.uniform(max(0,self.frequency_index -5), min(self.max_index,self.frequency_index + 5  , self.frequency_index )) )
    
    #self.frequency_index_two = math.floor(random.uniform(max(0,self.frequency_index_two -5), min(self.max_index,self.frequency_index_two + 5  , self.frequency_index_two ))  )
    # print (f'mutate threshold  : {self.energy_threshold}')
    
      


    





