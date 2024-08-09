

"""
Gene : Frequency bounnds gene. Return 1 if True. True if f domain is in range of gene.


"""

version = 1.0
print (f"EnergyFrequencyBound [{version}]")

from marlin_brahma.genes.gene_root import *
import random, json, math



#{'min_f' : 130000, 'max_f': 150000}

class EnergyIndexBound(ConditionalRoot):
  def __init__(self,env=None,  gene_args = None):
    """[summary]

    :param env: [description], defaults to None
    :type env: [type], optional
    """
    
    #print (gene_args)
    super().__init__(condition='energy_index_bound', env=env)
    
    min_index = gene_args['f_index_min']
    max_index = gene_args['f_index_max']
    min_threshold = gene_args['delta_energy_min']
    max_threshold = gene_args['delta_energy_max']
    
    
    
    self.frequency_index = math.floor(random.uniform(min_index , max_index))   
    # self.energy_threshold = random.uniform(0.01, 0.15)  
    self.energy_threshold = random.uniform(0.01, 0.15)

  def __str__(self):
    description = {}
    overview = super().__str__()
    data = {
        "decision type" : "EnergyIndexBound",
        "frequency index" : self.frequency_index,
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
    stats = None
    bounds_data = derived_data.query_stats_freq_index(self.frequency_index, iter_start_time)
    stats = bounds_data.stats
    #print (stats)
    delta_f = 0
    delta_f = stats['max_energy'] - stats['min_energy']
    
   
   
    self.Start()
    self.state = 0

    # print (f'avg e : {avg_energy} {self.lower_frequency} - {self.upper_frequency}')
    # print (f'avg e : {avg_energy} {self.lower_frequency} - {self.upper_frequency}')
    if stats == None:
      # print (f'avg e : {avg_energy} {self.lower_frequency} - {self.upper_frequency}')
      # exit()
      pass

    else:
        # print (avg_energy)
        file_out = False
        if file_out:
          outfile_name = f'{self.frequency_index}__power.txt'
          with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/{outfile_name}', 'a+') as f:
            f.write(f'{iter_start_time} {avg_energy}\n')
          self.Safe()

        if delta_f > self.energy_threshold:
            # print (f'trigger {delta_f} > {self.energy_threshold}')
            return 1

        return 0

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
    
      


    





