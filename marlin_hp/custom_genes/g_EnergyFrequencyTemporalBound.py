#g_EnergyFrequencyTemporalBound



"""
Gene : Frequency bounnds gene. Return 1 if True. True if f domain is in range of gene.


"""

version = 1.0
print (f"EnergyFrequencyTemporalBound [{version}]")

from marlin_brahma.genes.gene_root import *
from datetime import timedelta
import random, json, math



#{'min_f' : 130000, 'max_f': 150000}

class EnergyFrequencyTemporalBound(ConditionalRoot):
  def __init__(self,env=None,  gene_args = None):
    """[summary]

    :param env: [description], defaults to None
    :type env: [type], optional
    """
    
    print (gene_args)
    
    super().__init__(condition='energy_frequency_bound', env=env)
    
    min_f  = gene_args['f_min']
    max_f  = gene_args['f_max']
    max_memory = gene_args['max_memory']
    print (f'max_memory {max_memory}')
    
    delta_energy_min =  gene_args['delta_energy_min']
    delta_energy_max =  gene_args['delta_energy_max']
    
    print (min_f,max_f)
    self.lower_frequency = math.floor(random.uniform(min_f,max_f))
    self.upper_frequency = math.floor(random.uniform(self.lower_frequency , max_f))
    self.memory = random.uniform(0 , max_memory) # ms
    self.delta_energy = random.uniform(delta_energy_min, delta_energy_max)  

  def __str__(self):
    description = {}
    overview = super().__str__()
    data = {
      "lower_frequency" : self.lower_frequency,
      "upper_frequency" : self.upper_frequency,
      "energy_threshold" : self.energy_threshold
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
    
    
    
    
    
    
    self.Start()
    self.state = 0


   
      # exit()

    geneInit = False
    
    # check init state
    sample_rate = data['sample_rate']
    current_data_index = data['data_index'] 
    current_data_delta_time = (current_data_index/sample_rate) * 1000 # ms
    # print (f'time from start: {current_data_delta_time} (ms)') 
    if current_data_delta_time > self.memory:
        geneInit = True
        
    if geneInit:
        
        self.Safe()
        
        energy_value = derived_data.query_energy_frames_at_frequency_bounds(self.lower_frequency,self.upper_frequency,iter_start_time)
        avg_energy = abs(energy_value[1])
         
        if avg_energy == 0:
            print (f'ERROR :: avg e : {avg_energy} {self.lower_frequency} - {self.upper_frequency}')
        
        avg_db = (energy_value[2])
        memory_ref_time = iter_start_time - timedelta(milliseconds=self.memory)
        energy_value = derived_data.query_energy_frames_at_frequency_bounds(self.lower_frequency,self.upper_frequency,memory_ref_time)
        avg_energy_ref = abs(energy_value[1])
        avg_db_ref = (energy_value[2])
        
        delta_energy = abs(avg_energy-avg_energy_ref)
        #print (f'{avg_energy} {avg_energy_ref} {delta_energy} {self.delta_energy}')
        
        # print (avg_energy)
        outfile_name = f'{self.lower_frequency}_{self.upper_frequency}_delta_power.txt'
        with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/{outfile_name}', 'a+') as f:
          f.write(f'{iter_start_time} {delta_energy}\n')
        
        if delta_energy > self.delta_energy:
            # print (f'trigger {avg_energy} > {self.energy_threshold}')
            return 1

        return 0



    return 0
  
  def mutate(self, data = {}):
    
    print (f'gene [energy_frequency_temporal_bound] mutating')
    # print (self.energy_threshold)
    # factor = random.uniform(-1,1)
    factor = 1
    factor = data['factor']
    creep_rate = data['creep_rate']
    
    #min_f
    self.lower_frequency = self.lower_frequency + (creep_rate*random.uniform(1,factor))
    #max_f
    self.upper_frequency = self.upper_frequency + (creep_rate*random.uniform(1,factor))
      
    self.lower_frequency = min(self.lower_frequency,self.upper_frequency)
    self.upper_frequency = max(self.lower_frequency,self.upper_frequency)
    
    self.delta_energy = self.delta_energy + (creep_rate*factor)
    
    
      


    





