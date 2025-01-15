
# datetime import
from datetime import datetime, timedelta
import math
import json
import random
import os, sys
import time
from rich.progress import Progress
from utils import *
import traceback
import pytz
from io_custom import *
# brahma
# IMPORT BRAHMA 
# import evolutionary procedures
import marlin_brahma.bots.bot_root as bots
import marlin_brahma.world.population as pop
from marlin_brahma.fitness.performance import RootDecision
import marlin_brahma.fitness.performance as performance
from marlin_brahma.evo.brahma_evo import *
# import threading
from multiprocessing import Process, Queue
# decision
# --- Define bespoke decision logic --
DECISION_FOLDER_USR = os.path.join('/','home','vixen', 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_decisions', '')
os.environ['DECISION_FOLDER_USR'] = DECISION_FOLDER_USR
sys.path.insert(0, os.environ['DECISION_FOLDER_USR'])

from custom_decisions import *
from custom_decisions import IdentEvaluation

gene_limits = None
with open("/home/vixen/rs/dev/marlin_hp/marlin_hp/gene_limits.json", 'r') as config_f:
    gene_limits = json.load(config_f)




class TracePrints(object):
  def __init__(self):    
    self.stdout = sys.stdout
  def write(self, s):
    self.stdout.write("Writing %r\n" % s)
    traceback.print_stack(file=self.stdout)
  def flush(self): pass


# sys.stdout = TracePrints()

class IdentGame(object):
 
    def __init__(self, application = None, data_manager = None, game_id = "", activation_level = 0.7):
        self.game = application
        print(self.game.data_feed)
        self.energy_tracker = {}
        self.data_manager = data_manager
        self.game_id = game_id
        self.bulk_energies = {}
        self.bulk_times = {}
        self.activation_level = activation_level
        
        
        self.active_features = {}
        
        self.run_stats = {}
        self.collect_stats = True
        
        self.number_run_idx = 0
        
    def world_step(self):
        pass
    
    def bot_step(self, bot = None, generation=0, listen_start_idx = 0, step_end_index = 0):
        if bot is not None:
            print (f'{bot.name} Start')
            print (bot)
            # reset data feed for new iteration
            #data_feed.reset()
            self.bulk_energies[bot.name] = {}
            total_iter_cnt = 0
            pressure_start = time.time()
            for env_pressure in self.game.data_feed:
                pressure_id = env_pressure.meta_data['snapshot_id']
                # print (f'Running {pressure_id} for {bot.name}')
                
                
                file_out = False
                #-- build spec
                if self.game.mode == 1 and self.game.bulk == 0:
                    file_out = True
                    print ("Setting out to True")
                    #build_f_profile(env_pressure, self.game_id, bot.name)
                    # build_spec(env_pressure, self.game_id,  bot.name)
                    # build_waveform(env_pressure, self.game_id, bot.name)
                
                
                # print (env_pressure)
                #build_spec(env_pressure, self.game_id,  bot.name)
                #build_f_profile(env_pressure, self.game_id, bot.name)
                
               
                
                #build_spec(env_pressure, self.game_id, bot.name)
                # build_waveform(env_pressure, self.game_id, bot.name)
                #print (env_pressure)
                # build_f_profile(env_pressure, self.game_id, bot.name)
                
                # xr_hits = self.game.derived_data.query_label_time(env_pressure.start_time, env_pressure.end_time)
                # print (xr_hits)
                
                
                
                listen_start_idx = 0
                listen_end_idx = 0
                
                
                
                
                # print (env_pressure.meta_data['snapshot_id'])
                listen_delta_idx = math.floor(self.game.algo_setup.args['listen_delta_t'] * env_pressure.meta_data['sample_rate'])
                
                
                env_pressure_length = 0
                if step_end_index == 0:
                    env_pressure_length = env_pressure.frequency_ts_np.shape[0]
                else:
                    env_pressure_length = step_end_index
                
                sample_rate = env_pressure.meta_data['sample_rate']
                energies = []
                times = []
                hits = [] # list of label hits for game mode 1
                idx_iter = 0
                listen_end_idx = 0
                
                
                feature_bot_names = {}
                
                while listen_start_idx < (env_pressure_length - listen_delta_idx):
                # while listen_start_idx < (env_pressure_length):
                    self.number_run_idx = max(self.number_run_idx, idx_iter)
                    # print (self.number_run_idx)
                    # --- get start & end slice idx ---
                    listen_end_idx = listen_start_idx + listen_delta_idx
                    slice_start = listen_start_idx
                    slice_end = min(listen_end_idx,env_pressure_length-1)
                    
                    # --- get datetime ---
                    _s = (slice_start / env_pressure.meta_data['sample_rate']) * 1000 # ms 
                    iter_start_time =  env_pressure.start_time + timedelta(milliseconds=_s)
                    # print (iter_start_time)
                    _s = (slice_end / env_pressure.meta_data['sample_rate']) * 1000
                    iter_end_time   =  env_pressure.start_time  + timedelta(milliseconds=_s)
                    #print (f'time vector bounds : {iter_start_time} : {iter_end_time}')
                    
                    # --- express bot ---
                    # [nb. data structure is passed to individual genes if dna is initialised.
                    # extra data can be added under 'init_data' field]
                    express_start = time.time()
                    # print (self.game.derived_data)
                    if self.game.mode == 1 and self.game.multiple_data != 1:
                        express_value = bot.ExpressDNA(data = {'data_index':listen_start_idx, 'sample_rate' : env_pressure.meta_data['sample_rate'] ,'current_data' :  env_pressure.frequency_ts_np.shape[slice_start:slice_end], 'derived_model_data' : self.game.derived_data, 'iter_start_time' : iter_start_time, 'iter_end_time' : iter_end_time})
                        # print (express_value)
                    if self.game.mode == 0:
                        # sys.stdout = TracePrints()
                        # print ('2')
                        express_value = bot.ExpressDNA(data = {'data_index':listen_start_idx, 'sample_rate' : env_pressure.meta_data['sample_rate'] ,'current_data' :  env_pressure.frequency_ts_np.shape[slice_start:slice_end], 'derived_model_data' : self.game.multiple_derived_data[pressure_id], 'iter_start_time' : iter_start_time, 'iter_end_time' : iter_end_time})
                    
                    if self.game.mode == 1 and self.game.multiple_data == 1:    
                        
                        express_value = bot.ExpressDNA(data = {'data_index':listen_start_idx, 'sample_rate' : env_pressure.meta_data['sample_rate'] ,'current_data' :  env_pressure.frequency_ts_np.shape[slice_start:slice_end], 'derived_model_data' : self.game.multiple_derived_data[pressure_id], 'iter_start_time' : iter_start_time, 'iter_end_time' : iter_end_time})
                    
                    express_end = time.time()
                    
                    
                    express_time = express_end - express_start
                    # print (f'time to express bot {express_time}')
                    express_level = bot.GetAvgExpressionValue()
                    # print (f'ex :  {express_level}')
                    
                    energies.append(express_level)
                    
                    # times.append(iter_end_time)
                    t_start_s = (slice_start / env_pressure.meta_data['sample_rate']) #
                    t_end_s = (slice_end / env_pressure.meta_data['sample_rate']) #
                    t_m = (t_start_s + t_end_s)/2                        
                    times.append(t_m)
                    
                    if express_level == 0:
                        express_level = random.uniform(0.05,0.1)
                    if express_level > 0.95:
                        express_level = random.uniform(0.95,1.0)
                   
                    if self.game.mode == 1 and self.game.bulk == 1:
                        # print (f'running : {idx_iter} | {bot.name}')
                        self.bulk_energies[bot.name][total_iter_cnt] = express_level
                        #print (iter_start_time)
                        #print (iter_start_time.strftime("%Y:%M:%d %H:%M:%S.%f +0000"))
                        date_string = iter_start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                        #utc_dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f %z')
                        #print (date_string)
                        
                        #self.bulk_times[idx_iter] = iter_start_time.strftime("%H:%M:%S.%f")
                        # print (iter_start_time.utcnow())
                        # utc_tz = pytz.timezone('UTC')
                        self.bulk_times[total_iter_cnt] = date_string
                        if float(express_level) > float(self.activation_level):
                            # print (f'adding active feature in time_frame : {idx_iter}')
                            if total_iter_cnt not in self.active_features:
                                self.active_features[total_iter_cnt] = []
                                # feature_bot_names[idx_iter] = []
                                
                            # if bot not in feature_bot_names[idx_iter]:
                                # feature_bot_names[idx_iter].append(bot.name)
                            self.active_features[total_iter_cnt].append(bot)
                                
                        # print (self.bulk_times[idx_iter])
                        idx_iter += 1
                        total_iter_cnt += 1
                    # --- transcription ---
                    # print (bot.transcriptionDNA.transcription_threshold)
                    transcription_data = {
                        'expression_data': bot.GetExpressionData(),
                    }
                    
                    transcribe_result = bot.transcriptionDNA.transcribe(transcription_data, self.activation_level)

                    
                   
                    # print (express_level)
                    # # Build labeled dataset here in order to view in spectrogrma image
                    #-----
                    if self.game.mode == 1:
                        xr_hits = self.game.derived_data.query_label_time(iter_start_time, iter_end_time)
                        if len(xr_hits) > 0:
                            hits.append(1)
                        else:
                            hits.append(0)
                

                    
                    # transcribe_result = True # force transcription
                    # ======Decision & Marking=========================
                    # --- make and add decision ---
                    if transcribe_result:
                        # print ("decision made")
                        decision_args = {
                            'status' : 1,
                            'env' : self.game.algo_setup.args['env'],
                            'iter_start_time' : iter_start_time,
                            'iter_end_time' : iter_end_time,
                            'action' : 1,
                            'type' : "MARLIN Ident",
                            'xr' : -1,
                            'epoch' : pressure_id
                        }
                        
                        record_decision = {
                            'env' : self.game.algo_setup.args['env'],
                            'type' : "MARLIN Ident",
                            'epoch' : pressure_id
                        }
                        
                        new_decision = IdentDecision(decision_data=decision_args)
                        self.game.performance.add_decision(decision=new_decision, epoch = env_pressure.meta_data['snapshot_id'], botID = bot.name)
                        
                        self.all_decisions[iter_start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")] = record_decision
                        # ================================================
                        # query dataset to mark decision
                        # ================================================
                        
                        
                        xr = False
                        bulk = 0
                        if hasattr(self.game, 'bulk'):
                            bulk = self.game.bulk
                        
                        if bulk == 0:
                            
                            if self.game.mode == 0 or self.game.mode == 1 :
                                # print ('check decisions')
                                #--- traditional
                                xr_hits = self.game.derived_data.query_label_time(iter_start_time, iter_end_time)
                                if len(xr_hits) > 0:
                                    print (xr_hits)
                                    xr_data = xr_hits[0]
                                    if xr_data['xr'] == True:
                                        # print ("Success")
                                        # print (xr_data)
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
                            'type' : "MARLIN Ident",
                            'xr' : xr,
                            'epoch' : pressure_id
                        }
                        
                        close_decision = IdentDecision(decision_data=decision_args)                    
                        self.game.performance.add_decision(decision=close_decision, epoch = env_pressure.meta_data['snapshot_id'], botID = bot.name)
                        
                    # =================================================
                    
                    # update listen start idx
                    listen_start_idx = listen_end_idx
                
                
                
                # pressure_end = time.time()
                # run_time = pressure_end - pressure_start
                # # print (f'number iters : {idx_iter}')
                # print (f'time to run [1] life : {run_time} {bot.name}')
                # print (f'time to express : {express_time} {bot.name}')
                outfile_name = f'{pressure_id}_{bot.name}.out' 
                console_name= f'{pressure_id}_{bot.name}_console.txt'
                decision_name = f'{pressure_id}_{bot.name}_decisions.csv'
                
                # print (outfile_name)
                # --- RUN MODEL FROM WEB APP DATA
                # file_out = False
                
                # op_out = True
                # if op_out:
                    
                #     decision_text = self.game.performance.showBotDecisions(bot_name=bot.name)
                #     print (decision_text)
                #     with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/decision_out/{decision_name}', 'w') as f:
                #         f.write(decision_text)
                        
                    
                # print (f'fileout {file_out}')
                # print (f'bulk {self.game.bulk}')
                # print (f'mode {self.game.mode}')
                # exit()
                
                
                if file_out:
                    
                    
                    
                    decision_text = self.game.performance.showBotDecisions(bot_name=bot.name)
                    # print (decision_text)
                    
                    with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/{decision_name}', 'w') as f:
                        f.write(decision_text)
                    
                    with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/{outfile_name}', 'w') as f:
                        if self.game.mode == 1:
                            f.write(f"time,energy\n")
                        for i in range(0,len(energies)):
                            e = energies[i]
                            t = times[i]
                            if e == 0:
                                e = random.uniform(0.05,0.2)
                                energies[i] = e
                            if e > 0.8:
                                e = random.uniform(0.8,1.0)
                                energies[i] = e
                            if self.game.mode == 1:
                                f.write(f"{t},{e}\n")
                            else:
                                f.write(f"{t} {e}\n")

                   
                    
                    build_spec(env_pressure, self.game_id,  bot.name, times=times, energies=energies, hits = hits, activation_level=self.activation_level)
                    
                    
                if self.game.mode == 1:
                    result_data = {}
                    result_data['energies'] = f'https://vixen.hopto.org/rs/ident_app/ident/brahma/out/{outfile_name}'
                    result_data['console'] = f'https://vixen.hopto.org/rs/ident_app/ident/brahma/out/{console_name}'
                    #print ((result_data))
                    # print (f'https://vixen.hopto.org/rs/ident_app/ident/brahma/out/{outfile_name}')
                # --- RUN MODEL FROM WEB APP DATA
            
            
            
            pressure_end = time.time()
            run_time = pressure_end - pressure_start
            # print (f'number iters : {idx_iter}')
            print (f'time to run [1] life : {run_time} {bot.name}')
            # print (f'{bot.name} Done')
            
            op_out = False
            bulk = 0
            if hasattr(self.game, 'bulk'):
                bulk = self.game.bulk
            if op_out and bulk == 0:
                
                decision_text = self.game.performance.showBotDecisions(bot_name=bot.name, verbose=False     )
                

                decision_name = f'{bot.name}_{generation}_decisions.csv'
                with open(f'/home/vixen/html/rs/ident_app/ident_gui/brahma/out/decision_out/{decision_name}', 'w') as f:
                    f.write(decision_text)
             
             
    def run_bot_mt(self, sub_filename = "", start_idx=0, end_idx=0, filename=""):
        self.mt_bulk_energies = {}
        self.mt_bulk_times = {}
        mt_res = []
        print ("Running Live")
        
        self.game.generation_reset()
        
        n = 15
        
        # apply thread
        # print (list(self.game.loaded_bots.keys()))
        feature_ids = list(self.game.loaded_bots.keys())
        number_bots = len(feature_ids)
        # print (f'number {number_bots}')
        delta_f = math.floor(number_bots/n)
        # print (f'd : {delta_f}')
        threads = []
        
        
        
        Q = Queue()
        for i in range(0,n):
            mt_bots = {}
            for j in range((i*delta_f),((i*delta_f)+delta_f)):
                if j < number_bots:
                    # print (j)
                    # print (f'{(i*(i+delta_f))} : {((i*(i+delta_f))+delta_f)}')
                    mt_bots[feature_ids[j]]=self.game.loaded_bots[feature_ids[j]]

            # x = threading.Thread(target= self.inner_bot_run_mt, args=(mt_bots,i,))
            # print (list(mt_bots.keys()))
            # print (mt_bots)
            if len(mt_bots) > 0:
                x = Process(target= self.inner_bot_run_mt, args=[mt_bots,i, Q, start_idx, end_idx])
                x.start()
                threads.append(x)
        
       
        for i in range(len(threads)):
            
            #resultdict.update(Q.get())
            mt_res.append(Q.get())
            
        
        for thread in threads:
            # print ('joining threads')
            thread.join()
            thread.terminate()
        
        
        for r in mt_res:
            energy_data = r['e']
            for k,v in energy_data.items():
                self.bulk_energies[k] = v
        
        for r in mt_res:
            a_f = r['af']
            for k,f in a_f.items():
                if k not in self.active_features:
                    self.active_features[k] = []
                    
                for feature in f:
                    self.active_features[k].append(feature)
                    
        
        
        #print (mt_res)
        self.bulk_times = mt_res[0]['t']
        self.number_run_idx = mt_res[0]['idx']
        # and back         
        # may need to join
        # print ('writing files')
        # print (self.bulk_energies)
        #dump bulk energies if exist
        # with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/group_energies_{self.game.ss_ids[0]}.json', 'w+') as f:
        with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/group_energies_{filename}.json', 'w+') as f:
            json.dump(self.bulk_energies,f)  
        
        # with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/group_times_{self.game.ss_ids[0]}.json', 'w+') as f:
        with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/group_times_{filename}.json', 'w+') as f:
            json.dump(self.bulk_times,f)  
        
        
        update_run(filename,10)   
        #self.data_manager.closeRun(0)
              
    
    def inner_bot_run_mt(self, mt_bots, thread_id, Q, step_start_idx=0, step_end_idx=0):
        
        
        number_run = 0
        self.all_decisions = {}
        run_n = 0
        for bot_name, bot in mt_bots.items():
            
            # print(f'run numbr : {run_n}')
            # try:
            # print(f'thread id : {thread_id}')
            iter_res = self.bot_step(bot,listen_start_idx = step_start_idx, step_end_index = step_end_idx)
            # print (f'bulk data counter : {len(self.bulk_energies)}')
            # except:
            #     print ("erro")
            run_n += 1 
        #return [self.bulk_energies, self.bulk_times]
        # Q.put(self.bulk_energies, self.bulk_times) 
        res =  {
            'e' : self.bulk_energies,
            't' : self.bulk_times,
            'af' : self.active_features,
            'idx' : self.number_run_idx
        }    
        
        Q.put(res)              
               
    def run_bots(self, sub_filename="", start_idx=0, end_idx=0, filename="", out_path=""):
        # print("*** Running Live ***")
        self.game.generation_reset()

        number_run = 0
        self.all_decisions = {}
        # with Progress() as progress:
        #     process = psutil.Process(os.getpid())
        #     task1 = progress.add_task(
        #         f"[green] Running features/bots against your data", total=len(list(self.game.loaded_bots.keys())))

        for bot_name, bot in self.game.loaded_bots.items():
            # try:
            iter_res = self.bot_step(
                bot, listen_start_idx=0, step_end_index=0)
            # except:
            #     print ("erro")
            # progress.update(task1, advance=1)

        # dump bulk energies if exist
        # with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/group_energies_{self.game.ss_ids[0]}.json', 'w+') as f:
        with open(f'{out_path}/group_energies_{self.game_id}.json', 'w+') as f:
            json.dump(self.bulk_energies, f)

        # with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/group_times_{self.game.ss_ids[0]}.json', 'w+') as f:
        with open(f'{out_path}/group_times_{self.game_id}.json', 'w+') as f:
            json.dump(self.bulk_times, f)

        #! update
        # update_run(self.game_id, 10)
        # self.data_manager.closeRun(0)

    def run_bot(self):
        print ("Running Live")
        self.game.generation_reset()
        
        
        
        number_run = 0
        self.all_decisions = {}
        for bot_name, bot in self.game.loaded_bots.items():
            # try:
            iter_res = self.bot_step(bot)
            # except:
            #     print ("erro")
                          
    
        #dump bulk energies if exist
        # with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/group_energies_{self.game.ss_ids[0]}.json', 'w+') as f:
        with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/group_energies_{self.game_id}.json', 'w+') as f:
            json.dump(self.bulk_energies,f)  
         
        # with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/group_times_{self.game.ss_ids[0]}.json', 'w+') as f:
        with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/group_times_{self.game_id}.json', 'w+') as f:
        
            json.dump(self.bulk_times,f)  
        
        
        update_run(self.game_id,10)   
        #self.data_manager.closeRun(0)
        
            
    def play(self):
        
        for op_run in range(1,10):
        
            number_generations = self.game.algo_setup.args['number_generations'] 
            number_bots = self.game.algo_setup.args['population_size']
            with Progress() as progress:
                for generation_number in range(0, self.game.algo_setup.args['number_generations']):

                    print (f'Generation {generation_number} of {number_generations}')
                    # build generational performance management
                    self.game.generation_reset()
                    generation_start_time = time.time()
                    task1 = progress.add_task("[red]Running features (bots)...", total=self.game.algo_setup.args['population_size'])
                
                    for individual_idx in range(0, self.game.algo_setup.args['population_size']):
                        progress.update(task1, advance=1)
                        #print (f'Bot: {individual_idx} of {number_bots}')
                        # get bot name
                        bot_name = self.game.population.bots[individual_idx]
                        
                        # debug -> bot data
                        #_bot = self.game.population.species[bot_name]
                        #print (_bot.printStr())
                        if bot_name in self.game.population.species:
                            iter_res = self.bot_step(self.game.population.species[bot_name])
                        else: 
                            print (f'CRITICAL: bot not found in species list. Has it been removed? Generation: {generation_number}')
                    
                    generation_end_time = time.time()
                    generation_run_time = generation_end_time-generation_start_time
                    # print (f'Generation run time {generation_run_time}')
                    #self.dump_bot_energies(generation_number)

                    # print decisions
                    
                    
                    self.game.performance.evaluateBots(self.game.population.species,self.game.algo_setup.args)
                    best_fitness, worst_fitness, winner_id = self.game.performance.text_output_fitness()
                    print (f'best : {best_fitness} : {worst_fitness}, {winner_id}')
                    
                    fitness_vector = []
                    fitness_vector = self.game.performance.output_fitness_vector()
                    #print(fitness_vector)
                    
                    if best_fitness > 0.0:
                        self.game.performance.showBotDecisions(bot_name=winner_id)
                    with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/gen_out_best.txt', 'a+') as f:
                        f.write(f'data {generation_number} {best_fitness}\n')
                    with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/gen_out_worst.txt', 'a+') as f:
                        f.write(f'data {generation_number} {worst_fitness}\n')
                    
                    # output all fitness
                    with open(f'/home/vixen/html/rs/ident_app/ident/brahma/out/all_fitness.txt', 'a+') as f:
                        for fitness in fitness_vector:
                            f.write(f"{fitness}\n")
                        f.write("-\n")
                    
                    #record performance
                    print ("output and record data")
                    #self.game.performance.outputAndRecordEvalResults(dataManager =  self.data_manager, gen = generation_number, population=self.game.population.species)
                    # print decisions
                    if best_fitness > 0:
                        winningBots = [winner_id]
                        self.data_manager.recordWinningBots(winningBots, self.game.population.species, save_name=f'{winner_id}_{generation_number}')
                        self.data_manager.saveWinningBots(winningBots, self.game.population.species, final = False, new_name=f'{winner_id}_{generation_number}')
                        
                    #evolve
                    
                    self.selection_pressure()
                
                
                
                
                
                self.data_manager.setStatus(1)
                myTournament = None
                
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
    