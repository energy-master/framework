

"""
Gene : Frequency bounnds gene. Return 1 if True. True if f domain is in range of gene.


"""

version = 1.0
print (f"EnergyProfileFluxIndex [{version}]")

from marlin_brahma.genes.gene_root import *
import random, json, math
import statistics


#{'min_f' : 130000, 'max_f': 150000}

class EnergyProfileFluxIndex(ConditionalRoot):
    
  def __init__(self,env=None,  gene_args = None):
    """[summary]

    :param env: [description], defaults to None
    :type env: [type], optional
    """
    
    #print (gene_args)
    super().__init__(condition='EnergyProfileFluxIndex', env=env)
    
    min_index = gene_args['f_index_min']
    max_index = gene_args['f_index_max']
    
    
    
    flux_multiple_min_pc = gene_args['flux_multiple_min_pc']
    flux_multiple_max_pc = gene_args['flux_multiple_max_pc']
    
    self.frequency_index = math.floor(random.uniform(min_index , max_index))   
    # print (self.frequency_index)
    self.flux_multiple_pc = random.uniform(flux_multiple_min_pc,flux_multiple_max_pc)
    max_memory = gene_args['max_memory']
    min_memory = gene_args['min_memory']
    # self.memory = math.floor(random.uniform(min_index , max_index))  
    self.memory = random.uniform(min_memory , max_memory)
    
    self.energy_profile = []
    
    self.last_active_index = 0
    
  def __str__(self):
    
  
    description = {}
    overview = super().__str__()
    data = {
        "decision type" : "EnergyProfileFluxIndex",
        "frequency index" : self.frequency_index,
        "flux_multiple" : self.flux_multiple_pc,
        "memory" : self.memory
        
    }
    
    description['overview'] = overview
    description['data'] = data
    
    return ((description))
    


  def run(self, data = {}):
    import math
    
    if not hasattr(self, 'last_active_index'):
      # print ('no att')
      self.last_active_index = 0
    else:
      # print ('att')
      pass
    
    avg_energy = 0
    
    # check init state
    sample_rate = data['sample_rate']
    current_data_index = data['data_index'] 
    current_data_delta_time = ((current_data_index-self.last_active_index)/sample_rate) * 1000 # ms
    
    geneInit = False
    
    if hasattr(self,'memory') == False:
      self.memory = 0
    
    if current_data_delta_time > self.memory:
          geneInit = True
    else:
          return 0
    
    # get f at timestamps
    derived_data = data['derived_model_data']
    iter_start_time = data['iter_end_time']
    stats = None
    bounds_data = derived_data.query_stats_freq_index(self.frequency_index, iter_start_time)
    stats = bounds_data.stats
    #print (stats)
    # delta_f = 0
    # delta_f = stats['max_energy'] - stats['min_energy']
    delta_flux = 0
    if 'max_energy' in stats:
        
        spot_energy =  stats['max_energy'] 
        self.energy_profile.append(stats['max_energy'])

       
    else:
        
        return 0
    
    # if len(self.energy_profile) > 100:
    profile_avg = statistics.mean(self.energy_profile)
    delta_flux = float(((spot_energy - profile_avg) / profile_avg)) * 100
    # print (delta_flux)
   
   
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
          with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/perc.csv', 'a+') as f:
            f.write(f'{iter_start_time}, {self.memory}, {profile_avg}, {spot_energy} , {delta_flux}\n')
          self.Safe()

        if delta_flux > self.flux_multiple_pc:
            # print (f'trigger {delta_f} > {self.energy_threshold}')
            self.energy_profile = []
            self.last_active_index = current_data_index
            return 1

        return 0

    return 0
  
  def mutate(self, data = {}):
    
    # print (f'gene [energy_frequency_bound] mutating')
    # print (self.energy_threshold)
    factor = random.uniform(-1,1)
    #factor = 1
    creep_rate = data['pc_threshold_creep_rate']
    
    # #min_f
    # self.lower_frequency = self.lower_frequency + (creep_rate*random.uniform(1,factor))
    # #max_f
    # self.upper_frequency = self.upper_frequency + (creep_rate*random.uniform(1,factor))
      
    # self.lower_frequency = min(self.lower_frequency,self.upper_frequency)
    # self.upper_frequency = max(self.lower_frequency,self.upper_frequency)
    
    self.flux_multiple_pc = self.flux_multiple_pc + (creep_rate*factor)
    # print (f'mutate threshold  : {self.energy_threshold}')
    
      


    





