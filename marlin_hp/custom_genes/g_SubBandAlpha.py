

"""
Gene : Frequency bounnds gene. Return 1 if True. True if f domain is in range of gene.


"""

version = 1.0
print (f"SubBand_alpha [{version}]")

from marlin_brahma.genes.gene_root import *
import random, json




class SubBandAlpha(ConditionalRoot):
  def __init__(self,env=None, gene_args={'min_f' : 130000, 'max_f': 150000}):
    """[summary]

    :param env: [description], defaults to None
    :type env: [type], optional
    """
    
    super().__init__(condition='SubBandAlpha', env=env)
    min_f  = gene_args['f_min']
    max_f  = gene_args['f_max']
    self.lower_frequency = random.uniform(min_f,max_f)
    self.upper_frequency = random.uniform(self.lower_frequency , max_f)
    # self.lower_frequency = 0
    # self.upper_frequency = 1000
    self.stdev_threshold = random.uniform(0,1)
    # self.energy_threshold = random.uniform(0, 100)  # db
   
  def __str__(self):
    # return (super().__str__())
    description = {}
    overview = super().__str__()
    data = {
      "lower_frequency" : self.lower_frequency,
      "upper_frequency" : self.upper_frequency,
      "stdev_threshold" : self.stdev_threshold
    }
    
    description['overview'] = overview
    description['data'] = data
    
    return ((description))
    
  def run(self, data = {}):
    import math
    return 0
    avg_energy = 0
    stdev_ratio = 0
    # get f at timestamps
    derived_data = data['derived_model_data']
    iter_start_time = data['iter_start_time']
    iter_end_time =  data['iter_end_time']
    
    #energy_value = derived_data.query_energy_frames_at_frequency_bounds(self.lower_frequency,self.upper_frequency,iter_start_time)
    #avg_energy = abs(energy_value[1])
    # print (iter_start_time)
    
    #logic
    stats = None
    # get subdomain energy profile
    # spectral_data = derived_data.query_band_energy_profile(iter_start_time, iter_end_time, self.lower_frequency, self.upper_frequency, False )
    spectral_data_frames = derived_data.query_band_energy_loaded_profile(iter_start_time, iter_end_time, self.lower_frequency, self.upper_frequency)
    dim_found = len(spectral_data_frames)
    # print (f'found : {dim_found}')
    
    # print (f'low: {self.lower_frequency} high: {self.upper_frequency} {iter_start_time}=>{iter_end_time}')
    if len(spectral_data_frames) == 0:
      return 0
    spectral_data = spectral_data_frames[0]
    #print (spectral_data.stats)
    

    if spectral_data != 0:
      
      stats = spectral_data.stats
      # print(spectral_data[1])
      
     
      
      # get min e and max e
      min_energy = stats['min_energy']
      max_energy = stats['max_energy']
      std_dev = stats['stdev']
      energy_range = abs(max_energy-min_energy)
      stdev_ratio = std_dev/energy_range
      
      if (energy_range == 0):
        energy_range = 0.01
      
      self.Start()
      self.state = 0
      
      
     


    if len(data) > 0:
       
        self.Safe()

        
        if stdev_ratio > self.stdev_threshold:

            return 1

        return 0

    return 0
  
  def mutate(self, data = {}):
    
    print (f'gene [energy_frequency_bound] mutating')
    
    factor = random.uniform(-10,10)
    creep_rate = data['creep_rate']
    
    #min_f
    self.lower_frequency = self.lower_frequency + (creep_rate*random.uniform(1,factor))
    #max_f
    self.upper_frequency = self.upper_frequency + (creep_rate*random.uniform(1,factor))
      
    self.lower_frequency = min(self.lower_frequency,self.upper_frequency)
    self.upper_frequency = max(self.lower_frequency,self.upper_frequency)
    
      


    





