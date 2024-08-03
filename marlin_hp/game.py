
# datetime import
from datetime import datetime, timedelta
import math
import json
import random
import os, sys

from utils import *

# brahma
# IMPORT BRAHMA 
# import evolutionary procedures
import marlin_brahma.bots.bot_root as bots
import marlin_brahma.world.population as pop
from marlin_brahma.fitness.performance import RootDecision
import marlin_brahma.fitness.performance as performance
from marlin_brahma.evo.brahma_evo import *


# decision
# --- Define bespoke decision logic --
DECISION_FOLDER_USR = os.path.join('/','home','vixen', 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_decisions', '')
os.environ['DECISION_FOLDER_USR'] = DECISION_FOLDER_USR
sys.path.insert(0, os.environ['DECISION_FOLDER_USR'])

from custom_decisions import *
from custom_decisions import IdentEvaluation

gene_limits = None
with open("gene_limits.json", 'r') as config_f:
    gene_limits = json.load(config_f)

print (gene_limits)


class IdentGame(object):
 
    def __init__(self, application = None, data_manager = None, game_id = ""):
        self.game = application
        print(self.game.data_feed)
        self.energy_tracker = {}
        self.data_manager = data_manager
        self.game_id = game_id
        
        
    def world_step(self):
        pass
    
    def bot_step(self, bot = None):
        if bot is not None:
                    
            # reset data feed for new iteration
            #data_feed.reset()
            
            for env_pressure in self.game.data_feed:
                
                #-- build spec
                if self.game.mode == 1:
                    print ("building image data")
                    build_f_profile(env_pressure, self.game_id, bot.name)
                    build_spec(env_pressure, self.game_id,  bot.name)
                    build_waveform(env_pressure, self.game_id, bot.name)
                    
                
                # print (env_pressure)
                #build_spec(env_pressure, self.game_id,  bot.name)
                #build_f_profile(env_pressure, self.game_id, bot.name)
                
               
                
                #build_spec(env_pressure, self.game_id, bot.name)
                # build_waveform(env_pressure, self.game_id, bot.name)
                #print (env_pressure)
                # build_f_profile(env_pressure, self.game_id, bot.name)
                
                # xr_hits = self.game.derived_data.query_label_time(env_pressure.start_time, env_pressure.end_time)
                # print (xr_hits)
                
                pressure_id = env_pressure.meta_data['snapshot_id']
                listen_start_idx = 0
                listen_end_idx = 0
                # print (env_pressure.meta_data['snapshot_id'])
                listen_delta_idx = math.floor(self.game.algo_setup.args['listen_delta_t'] * env_pressure.meta_data['sample_rate'])
                env_pressure_length = env_pressure.frequency_ts_np.shape[0]
                sample_rate = env_pressure.meta_data['sample_rate']
                energies = []
                times = []
                
                while listen_start_idx < (env_pressure_length - listen_delta_idx):
                    
                    # --- get start & end slice idx ---
                    listen_end_idx = listen_start_idx + listen_delta_idx
                    slice_start = listen_start_idx
                    slice_end = min(listen_end_idx,env_pressure_length-1)
                    
                    # --- get datetime ---
                    _s = (slice_start / env_pressure.meta_data['sample_rate']) * 1000 # ms 
                    iter_start_time =  env_pressure.start_time + timedelta(milliseconds=_s)
                    _s = (slice_end / env_pressure.meta_data['sample_rate']) * 1000
                    iter_end_time   =  env_pressure.start_time  + timedelta(milliseconds=_s)
                    print (f'time vector bounds : {iter_start_time} : {iter_end_time}')
                    
                    # print (f'DMM input vector size: {listen_delta_idx}')
                    # --- express bot ---
                    # [nb. data structure is passed to individual genes if dna is initialised.
                    # extra data can be added under 'init_data' field]
                    express_value = bot.ExpressDNA(data = {'data_index':listen_start_idx, 'sample_rate' : env_pressure.meta_data['sample_rate'] ,'current_data' :  env_pressure.frequency_ts_np.shape[slice_start:slice_end], 'derived_model_data' : self.game.derived_data, 'iter_start_time' : iter_start_time, 'iter_end_time' : iter_end_time})
                    express_level = bot.GetAvgExpressionValue()
                    print (f'e {express_level}')
                    energies.append(express_level)
                    times.append(iter_end_time)
                    
                    
                    # --- transcription ---
                    # print (bot.transcriptionDNA.transcription_threshold)
                    transcription_data = {
                        'expression_data': bot.GetExpressionData(),
                    }
                    
                    transcribe_result = bot.transcriptionDNA.transcribe(transcription_data)
                    
                    # transcribe_result = True # force transcription
                    # ======Decision & Marking=========================
                    # --- make and add decision ---
                    if transcribe_result:
                        print ("decision made")
                        decision_args = {
                            'status' : 1,
                            'env' : self.game.algo_setup.args['env'],
                            'iter_start_time' : iter_start_time,
                            'iter_end_time' : iter_end_time,
                            'action' : 1,
                            'type' : "HP Ident",
                            'xr' : -1
                        }
                        
                        new_decision = IdentDecision(decision_data=decision_args)
                        self.game.performance.add_decision(decision=new_decision, epoch = "1", botID = bot.name)
                        
                        
                        # ================================================
                        # query dataset to mark decision
                        # ================================================
                        
                        
                        xr = False
                        if self.game.mode == 0:
                            
                            #--- traditional
                            xr_hits = self.game.derived_data.query_label_time(iter_start_time, iter_end_time)
                            if len(xr_hits) > 0:
                                xr_data = xr_hits[0]
                                if xr_data['xr'] == True:
                                    print ("Success")
                                    print (xr_data)
                                    xr = True
                            #--- energy
                            #energy_value = self.game.derived_data.query_energy_frames_at_frequency_bounds(137000,137500, iter_end_time)
                            # avg_energy = abs(energy_value[1])
                            # print (avg_energy)
                            # if avg_energy > 0.08:
                            #     xr = True
                            #     print (avg_energy)
                            #     print ("success")
                                
                            else:
                                xr = False
                            
                            # print (xr)
                            
                        
                    
                        # ================================================
                    
                        
                        decision_args = {
                            'status' : 0,
                            'env' : self.game.algo_setup.args['env'],
                            'iter_start_time' : iter_start_time,
                            'iter_end_time' : iter_end_time,
                            'action' : 0,
                            'type' : "HP Ident",
                            'xr' : xr
                        }
                        
                        close_decision = IdentDecision(decision_data=decision_args)                    
                        self.game.performance.add_decision(decision=close_decision, epoch = "1", botID = bot.name)
                        
                    # =================================================
                    
                    # update listen start idx
                    listen_start_idx = listen_end_idx
                
                outfile_name = f'{pressure_id}_{bot.name}.out' 
                console_name= f'{pressure_id}_{bot.name}_console.txt'
                
                # print (outfile_name)
                # --- RUN MODEL FROM WEB APP DATA
                with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/{outfile_name}', 'w') as f:
                    if self.game.mode == 1:
                        f.write(f"time,energy\n")
                    for i in range(0,len(energies)):
                        e = energies[i]
                        t = times[i]
                        
                        if self.game.mode == 1:
                            f.write(f"{t},{e}\n")
                        else:
                            f.write(f"{t} {e}\n")
                        
                if self.game.mode == 1:
                    result_data = {}
                    result_data['energies'] = f'https://vixen.hopto.org/rs/ident_app/ident/brahma/out/{outfile_name}'
                    result_data['console'] = f'https://vixen.hopto.org/rs/ident_app/ident/brahma/out/{console_name}'
                    print ((result_data))
                    # print (f'https://vixen.hopto.org/rs/ident_app/ident/brahma/out/{outfile_name}')
                # --- RUN MODEL FROM WEB APP DATA
                
                
    def run_bot(self):
        print ("Running Live")
        self.game.generation_reset()
        for bot_name, bot in self.game.loaded_bots.items():
            iter_res = self.bot_step(bot)
            
        self.data_manager.closeRun(0)
            
            
    def play(self):
        number_generations = self.game.algo_setup.args['number_generations'] 
        number_bots = self.game.algo_setup.args['population_size']
        
        for generation_number in range(0, self.game.algo_setup.args['number_generations']):

            print (f'Generation {generation_number} of {number_generations}')
            # build generational performance management
            self.game.generation_reset()
        
            for individual_idx in range(0, self.game.algo_setup.args['population_size']):
                print (f'Bot: {individual_idx} of {number_bots}')
                # get bot name
                bot_name = self.game.population.bots[individual_idx]
                
                # debug -> bot data
                _bot = self.game.population.species[bot_name]
                #print (_bot.printStr())
                
                iter_res = self.bot_step(self.game.population.species[bot_name])
            
                
            #self.dump_bot_energies(generation_number)

            # print decisions
            #self.game.performance.showBotDecisions()
            print ("Evualating finals...")
            self.game.performance.evaluateBots(self.game.population.species,self.game.algo_setup.args)
            best_fitness, worst_fitness, winner_id = self.game.performance.text_output_fitness()
            print (f'best : {best_fitness} : {worst_fitness}, {winner_id}')
            with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/gen_out_best.txt', 'a+') as f:
                f.write(f'data {generation_number} {best_fitness}\n')
            with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/gen_out_worst.txt', 'a+') as f:
                f.write(f'data {generation_number} {worst_fitness}\n')
            
            #record performance
            
            self.game.performance.outputAndRecordEvalResults(dataManager =  self.data_manager, gen = generation_number, population=self.game.population.species)
            # print decisions
            self.game.performance.showBotDecisions()
            
            #evolve
            self.selection_pressure()
        
        
        self.data_manager.setStatus(1)
        myTournament = None
        print ("final tournament")
        myTournament = SimpleTournamentRegenerate(generationEval = self.game.performance.evaluation, population = self.game.population, dataManager = None)
        winningBots = myTournament.RankPopulation(output=1)
        print (winningBots)
        print ("Updating optimisation as complete.")
        self.data_manager.closeRun(len(winningBots))
        
        
        try:
            # --- Record winning bots
            print ("Recording winning bots...")
            self.data_manager.recordWinningBots(winningBots, self.game.population.species)
            print ("Recording winning bots...DONE")
        except:
            print ("Saving DB Error")
            
        try:  
            # --- Save winning bots
            print ("Save winning bots...")
            self.data_manager.saveWinningBots(winningBots, self.game.population.species, final = True)
            print ("Save winning bots...DONE")
        except:
            print ("Saving File Error")
                    


    def selection_pressure(self):
        
        """

        Evolution Step 1.
        =============================================
        All the bots have now been evaluated. The bots now compete in a tournament and are ranked. 
        Once ranked, the bot population is regernated. There are a number of ways of doing this. BrahmA
        root structures provide a quick development environment for getting the AI engine off the ground.
        BrahmA provides more sophisticated algorithms and custom algos can also be used. Be sure
        to derive your class definitions from the correct root structures.

        We will use a simple tournament/rank and regeneration algorithm.


        Step 1. Create the Tournament structure and compete.

        """ 
        myTournament = None
        myTournament = SimpleTournamentRegenerate(generationEval = self.game.performance.evaluation, population = self.game.population, dataManager = None)

        """

        Step 2. Tournament Rank

        """

        myTournament.RankPopulation()
        
        
        
        
        """

        Step 3. Regenerate Population
        Here bots are killed, children are created and the population of bots is 
        regenerated.

        """

        myTournament.RegeneratePopulation()
        
        """
        Step 4. The Genetic Shuffle
        Mutation plays a very significant role in evolution by altering gene points within the 
        genome.
        """

        genetic_shuffle = RootMutate(population = self.game.population, config = self.game.algo_setup.args )
        genetic_shuffle.mutate(args=self.game.algo_setup.args)
        
                
        #---generate list of zeros
        
        zeros = myTournament.Zeros()

        #---kill list of zeros
        self.game.population.KillDeadWood(tags = zeros) #--------------------------------

        #---regenerate population
        self.game.population.Repopulate(species="AcousticBot") #--------------------------------
        

        myTournament = None



        

  
    # I/O
    
    def dump_bot_energies(self, generation : int = 0):
        energy_list_gen = []
        for bot_name in self.game.population.bots:
           
            bot = self.game.population.species[bot_name]
            e = bot.GetAvgExpressionValue()
            
            if bot_name in self.energy_tracker:
            
                if e < 0.1:
                    e = random.uniform(0,0.15)
                
                else:
                    if e == self.energy_tracker[bot_name]:
                        dice = random.random()
                        if dice < 0.5:
                            e += random.uniform(0.05,0.1)
            else:
                
                self.energy_tracker[bot_name] = e
                
            energy_list_gen.append(e)
        # with open(f'output/energies_{generation}.json', "w") as f:
        #     json.dump(energy_list_gen,f)
            
class GameSim(object):
    
    def __init__(self, application = None):
        self.game = application
        
    
    def load_bots(self):
        pass
    
    def run_game(self):
        pass
    