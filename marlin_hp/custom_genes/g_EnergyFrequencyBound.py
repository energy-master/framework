

"""
Gene : Frequency bounnds gene. Return 1 if True. True if f domain is in range of gene.


"""

version = 1.0
print (f"EnergyFrequencyBound [{version}]")

from marlin_brahma.genes.gene_root import *
import random, json



#{'min_f' : 130000, 'max_f': 150000}

class EnergyFrequencyBound(ConditionalRoot):
  def __init__(self,env=None,  gene_args = None):
    """[summary]

    :param env: [description], defaults to None
    :type env: [type], optional
    """
    print ("building f")
    print (gene_args)
    super().__init__(condition='energy_frequency_bound', env=env)
    
    min_f  = gene_args['f_min']
    max_f  = gene_args['f_max']
    print (min_f,max_f)
    self.lower_frequency = random.uniform(min_f,max_f)
    self.upper_frequency = random.uniform(self.lower_frequency , max_f)
    # self.upper_frequency = 137500
    # self.lower_frequency = 137000
    
    
    self.energy_threshold = random.uniform(0.01, 0.15)  

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
    
    energy_value = derived_data.query_energy_frames_at_frequency_bounds(self.lower_frequency,self.upper_frequency,iter_start_time)
    avg_energy = abs(energy_value[1])
    avg_db = (energy_value[2])
   
    self.Start()
    self.state = 0

    # print (f'avg e : {avg_energy} {self.lower_frequency} - {self.upper_frequency}')
    # print (f'avg e : {avg_energy} {self.lower_frequency} - {self.upper_frequency}')
    if avg_energy == 0:
      print (f'avg e : {avg_energy} {self.lower_frequency} - {self.upper_frequency}')
      exit()

    if len(data) > 0:
        # print (avg_energy)
        outfile_name = f'{self.lower_frequency}_{self.upper_frequency}_power.txt'
        with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/{outfile_name}', 'a+') as f:
          f.write(f'{iter_start_time} {avg_energy}\n')
        self.Safe()

        if avg_energy > self.energy_threshold:
            # print (f'trigger {avg_energy} > {self.energy_threshold}')
            return 1

        return 0

    return 0
  
  def mutate(self, data = {}):
    
    print (f'gene [energy_frequency_bound] mutating')
    print (self.energy_threshold)
    # factor = random.uniform(-1,1)
    factor = 1
    creep_rate = data['creep_rate']
    
    #min_f
    self.lower_frequency = self.lower_frequency + (creep_rate*random.uniform(1,factor))
    #max_f
    self.upper_frequency = self.upper_frequency + (creep_rate*random.uniform(1,factor))
      
    self.lower_frequency = min(self.lower_frequency,self.upper_frequency)
    self.upper_frequency = max(self.lower_frequency,self.upper_frequency)
    
    self.energy_threshold = self.energy_threshold + (creep_rate*factor)
    print (f'mutate threshold  : {self.energy_threshold}')
    
      


    





