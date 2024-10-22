## 
# ===================================================
# | Harbour Popoise Detection Genetic Algorithm     |
# ===================================================
#
#
#
#  c. Rahul Tandon, 2024, RSA 2024 
#  GA Game to be presented in all teams July meeting.
#  version - october presentation 2.0
##
import sys
print (sys.argv[0])
command = False

if (len(sys.argv) > 1):
    user = sys.argv[1]
    snapshot_id =  sys.argv[2]
    bot_id = sys.argv[3]
    location_str = sys.argv[4]
    command = True
    

# --------------------------------------------------------------
# --- Imports ---                                          |
# --------------------------------------------------------------
from optimisation_manager import *
# sys, os imports
import sys,os, pickle


# marlin data import -- CUSTOM --
# sys.path.append('../../marlin_data/marlin_data')
sys.path.append('/home/vixen/rs/dev/marlin_data/marlin_data')
from marlin_data import *

# datetime import
from datetime import datetime, timedelta
from datetime import datetime as dt
# dotenv and pretty text
from dotenv import load_dotenv, dotenv_values
import pickle
import inspect
from rich import pretty
from rich.console import Console
pretty.install()
from rich import print as rprint
from rich.progress import Progress

load_dotenv()
config = dotenv_values("/home/vixen/rs/dev/marlin_hp/marlin_hp/marlin_hp.env")
logging.basicConfig(level=logging.INFO)
print (config)

# file paths and BRAHMA -- CUSTOM --\

# add application root to path
app_path = config['APP_DIR']
sys.path.insert(0, app_path)

# add brahma to system path
brahma_path = config['BRAHMA_DIR']
sys.path.insert(0, brahma_path)

# Define location of bespoke genes
GENETIC_DATA_FOLDER_USR = os.path.join('/','home','vixen', 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_genes', '')
os.environ['GENETIC_DATA_FOLDER_USR'] = GENETIC_DATA_FOLDER_USR
sys.path.insert(0, os.environ['GENETIC_DATA_FOLDER_USR'])

# Define location of bespoke bots
BOT_DATA_FOLDER_USR = os.path.join('/','home','vixen', 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_bots', '')
os.environ['CUSTOM_BOT_FOLDER_USR'] = BOT_DATA_FOLDER_USR
sys.path.insert(0, os.environ['CUSTOM_BOT_FOLDER_USR'])

# Define bespoke decision logic
DECISION_FOLDER_USR = os.path.join('/','home','vixen', 'rs','dev', 'marlin_hp', 'marlin_hp', 'custom_decisions', '')
os.environ['DECISION_FOLDER_USR'] = DECISION_FOLDER_USR
sys.path.insert(0, os.environ['DECISION_FOLDER_USR'])

NUMBA_CACHE_DIR = os.path.join('/','home','vixen', 'rs','dev', 'marlin_hp', 'marlin_hp', 'cache')
os.environ['NUMBA_CACHE_DIR'] = NUMBA_CACHE_DIR
# IMPORT BRAHMA 
# import evolutionary procedures
import marlin_brahma.bots.bot_root as bots
import marlin_brahma.world.population as pop
from marlin_brahma.fitness.performance import RootDecision
import marlin_brahma.fitness.performance as performance

#import app 
# from marlin_hp.custom_bots.mybots import *
from custom_bots import *
from custom_genes import *
from custom_decisions import *

# define data load path !- Don't add trailing "/" AND different path for sim and sig
simulation_data_path = "/home/vixen/rs/dev/marlin_hp/marlin_hp/data/sim"
signature_data_path = "/home/vixen/rs/dev/marlin_hp/marlin_hp/data/sig"

#import game code... always after main import headers ( especially sys path updates )
from game import *


#---brixham--- 
#"894385348205954020946277", -err
#sim_ids = ["149725199157732151251110","27576438198581074862571","331536168117870546723100","10065410156183055710193","298448815225760525793106","963118742699735308517278","27375678350083866014024","553063846482917121543419","607275917932749114463656","872949322189341025963541","21568196775422569759630","360852791896317614623842","50453828686617928438686","426073900994161246359981","536138136528390148468015","553063846482917121543419","607275917932749114463656","872949322189341025963541","21568196775422569759630","360852791896317614623842","50453828686617928438686","426073900994161246359981","536138136528390148468015"]
#stopped during 553063846482917121543419
#sim_ids = ["553063846482917121543419","607275917932749114463656","872949322189341025963541","21568196775422569759630","360852791896317614623842","50453828686617928438686","426073900994161246359981","536138136528390148468015"]

#snapshot ids - harbour porpoise
#sim_ids = ["595319575884544847440835","983040429874824099068136","496330765318343040702688","4510916050868080480725","791766822611366068898805","255909560907909230385506","147806043092917235813293","78166070127568866942302","842973085190946012464209","829104114451608323962914","98609866005174372621222","657840894015545578254694","186889183607954245154458","122544861653979922814199","746620378036255544838568","952470554636204171461253","84112867121113110266116","363225061427360721137730","892132173275665509527852","318396967157545581971621","356373695111556704055606","904312141590731430836451","48339782993708725612372","64750676209439611520678","82000738700746005197334","702347117716629389321406","250396319402307579582508","493774115372907090242973","194390376877680115920253","14268458523554600846434","434956021136141906386898","69649683436184019747768","44628814182950235636971","790960398526743855223705","13326721885126671142836","265674761255571576108244","597681256986802138994218","236106104873301048552682","916713239567735225362134","804031065014437941740813","291568429359273703023","36173624202566695107248","8479382645647189754988","16232091178931004631151","458216449030310996755802","644591713862472180785605","947001382799689346997018","392291757657498669254360","999641986773914295779102","398566267541751172139272","612544273941231236030105","708869496373649469644956","991813660211675758125747","839194952404431997544299","534392719420462600801900","798953357404557943447630","15352589773654034702565","114020915287240939545830","42437311049457749180813","958264056823172008798164","999876447769858733241497","222916752571191933551256","830598602900519976859006","99779383802341290531997"]
#sim_ids = ["983040429874824099068136","496330765318343040702688","4510916050868080480725"]
sim_ids = ["595319575884544847440835","711602635032502887898504"]
#sim_ids = ["711602635032502887898504"]
#sim_ids = ["983040429874824099068136","496330765318343040702688","4510916050868080480725"]
# err : ,"894385348205954020946277"
# sim_ids = ["331536168117870546723100","10065410156183055710193", "298448815225760525793106","963118742699735308517278","27375678350083866014024","553063846482917121543419", "607275917932749114463656","872949322189341025963541","21568196775422569759630","360852791896317614623842","50453828686617928438686"]

#sim_ids = ["520143795392987723411876","764890151895651769681344","45563595584322313756913","248470561894891192081873","402759887973510192835124","41727323791766549365593","647694228984103544257161","286319826116242051960787","329533822925273580800864","418916966169276935376041","139683296434342690620579","409521867080660511465981","914582940057539577250619","769903478672991740950863","270120439077230708879101","346556389230128492292821","29837675728197875153986","773179121166230611727721","794495194389540868352647","416712258283688252883225","23888683864171037778531","412097461438402312796334","694866831055824781152860","86632172854406208272180","690205431591207334685167","22157954742556305015231","913874664155139496706879","486149473818640999912065","149725199157732151251110","27576438198581074862571","426073900994161246359981","536138136528390148468015","326720943798167148590847","736656543121277229885055","18110274162517105662107","470419011514627776437887","168465643162113166293986","133214805115305710268752","577829282436642924314828","657234920621131539861726","130449751040357982627959","173692629870747521785339","227997043183601244526948","453170109404889801924174","470411384616622752078507","456584907395754021134235","733148934297347384934336","642553929648464099493279","192971751705391808170237","522776060487730369773036"]
#sim_ids = ["963118742699735308517278","27375678350083866014024","553063846482917121543419","607275917932749114463656"]



#sim_ids = ["711602635032502887898504","983040429874824099068136","496330765318343040702688","4510916050868080480725","791766822611366068898805","255909560907909230385506","147806043092917235813293","78166070127568866942302","842973085190946012464209","829104114451608323962914","98609866005174372621222","657840894015545578254694","186889183607954245154458","122544861653979922814199","746620378036255544838568","952470554636204171461253","84112867121113110266116","363225061427360721137730","892132173275665509527852","318396967157545581971621","356373695111556704055606","904312141590731430836451","48339782993708725612372","64750676209439611520678","82000738700746005197334","702347117716629389321406","250396319402307579582508","493774115372907090242973","194390376877680115920253","14268458523554600846434","434956021136141906386898","69649683436184019747768","44628814182950235636971","790960398526743855223705","13326721885126671142836","265674761255571576108244","597681256986802138994218","236106104873301048552682","916713239567735225362134","804031065014437941740813","291568429359273703023","36173624202566695107248","8479382645647189754988","16232091178931004631151","458216449030310996755802","644591713862472180785605","947001382799689346997018","392291757657498669254360","999641986773914295779102","398566267541751172139272","612544273941231236030105","708869496373649469644956","991813660211675758125747","839194952404431997544299","534392719420462600801900","798953357404557943447630","15352589773654034702565","114020915287240939545830","42437311049457749180813","958264056823172008798164","999876447769858733241497","222916752571191933551256","830598602900519976859006","99779383802341290531997","971461050187740241769345","59043452008554415790203","879267595290112763224531","586498933534706126389302", "803795664365219857193652"]
#sim_ids = ["952470554636204171461253","84112867121113110266116"]
limit = len(sim_ids)

sim_ids_data = {}
for s_id in sim_ids:
    sim_ids_data[s_id] = False

if command == True:
    sim_ids = []
    sim_ids.append(snapshot_id)
    print (sim_ids)
    

import os.path

s_id = sim_ids[0]

for s_id in sim_ids:
    if os.path.isfile(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/data/adapters/{s_id}.da'):
        sim_ids_data[s_id] = True
        

data_avail = False
for key, value in sim_ids_data.items():
    if value == False:
        data_avail = False
        break

print (f'data available: {data_avail} ')

if not data_avail:
    print ("More data required! Exiting..")
    print (sim_ids_data)
    # exit()

# force false
# data_avail = False


sim_ids = []
for s_id, value in sim_ids_data.items():
    if value == False:
        sim_ids.append(s_id)


# sim_ids = ["27375678350083866014024","553063846482917121543419"]
# sim_ids = ["595319575884544847440835"]
# sim_ids = ["983040429874824099068136"]

data_avail = True
sim_ids = ["711602635032502887898504","983040429874824099068136","496330765318343040702688","4510916050868080480725","791766822611366068898805","255909560907909230385506","147806043092917235813293","78166070127568866942302","842973085190946012464209","829104114451608323962914","98609866005174372621222","657840894015545578254694","186889183607954245154458","122544861653979922814199","746620378036255544838568","952470554636204171461253","84112867121113110266116","363225061427360721137730","892132173275665509527852","318396967157545581971621","356373695111556704055606","904312141590731430836451","48339782993708725612372","64750676209439611520678","82000738700746005197334","702347117716629389321406","250396319402307579582508","493774115372907090242973","194390376877680115920253","14268458523554600846434","434956021136141906386898","69649683436184019747768","44628814182950235636971","790960398526743855223705","13326721885126671142836","265674761255571576108244","597681256986802138994218","236106104873301048552682","916713239567735225362134","804031065014437941740813","291568429359273703023","36173624202566695107248","8479382645647189754988","16232091178931004631151","458216449030310996755802","644591713862472180785605","947001382799689346997018","392291757657498669254360","999641986773914295779102","398566267541751172139272","612544273941231236030105","708869496373649469644956","991813660211675758125747","839194952404431997544299","534392719420462600801900","798953357404557943447630","15352589773654034702565","114020915287240939545830","42437311049457749180813","958264056823172008798164","999876447769858733241497","222916752571191933551256","830598602900519976859006","99779383802341290531997","971461050187740241769345","59043452008554415790203","879267595290112763224531","586498933534706126389302", "803795664365219857193652"]
num_ids = len(sim_ids)
print (f'ids : {num_ids}')
n=0
print (n*(math.floor(num_ids/4)))
print (math.floor(n*(math.floor(num_ids/4)))+math.floor(num_ids/6))

sim_ids = sim_ids[math.floor(n*(math.floor(num_ids/4))):math.floor(n*(math.floor(num_ids/4)))+math.floor(num_ids/4)]
#sim_ids = ["711602635032502887898504"]
print (sim_ids)


limit = len(sim_ids)
print (f'number : {limit}')

# --------------------------------------------------------------
# --- Setup Class ---                                          |
# --------------------------------------------------------------

class AlgorithmSetup(object):
    """Class to control optimisation algorithm.

    Args:
        object (): root class object
    """     
    def __init__(self, config_file_path : str = "config.json"):
        
        self.args = {}
        
        #load config file
        run_config = None
        with open(config_file_path, 'r') as config_f:
            run_config = json.load(config_f)
            
        if run_config is not None:
           self.args = run_config
           
           
# --------------------------------------------------------------
# --- Main Application Class ---                               |
# --------------------------------------------------------------

class SpeciesIdent(object):
    """_summary_

    Args:
        object (_type_): _description_
    """    
    def __init__(self, setup : AlgorithmSetup = None):
        self.algo_setup = setup
        id =  random.randint(0,99999)
        self.batch_id = f'brahma_{id}'
        self.population = None
        self.data_feed = None
        self.derived_data = None
        # performance and evaluation
        self.performance = None
        self.algo_setup.args['run_id'] = self.batch_id
        self.loaded_bots = {}
        self.mode = 0
        self.multiple_derived_data = None
    
    def generation_reset(self):
        # print ("reseting generation data")
        self.performance = None
        self.performance = performance.Performance()
        self.performance.showBotDecisions()
        # print ("reseting generation data...done")
        
       
    def run(self):
        pass
    
    def build_world(self):
        """Build the population of bots using brahma_marlin. Genes are present in ../genes
        """
        
        try:
            logging.critical('Building population')
            self.population = pop.Population(parms=self.algo_setup.args, name="hp_classifier", gene_args = gene_limits)
            logging.critical('Building... ')

            self.population.Populate(species="AcousticBot", args = None)

            logging.debug("Population built")
        except Exception as err:
            logging.critical(f'Error building population {err=} {type(err)=}')
        
        
        
    def evolve_world(self):
        pass
    
    def output_world(self):
        pass
      
# --------------------------------------------------------------
# --- Entry Function ---                                       |
# --------------------------------------------------------------

rprint ("Building World")
# if __name__ == "__main__":
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)
rprint(f'Logging Level : {logger.level}')

rprint ("Creating algorithm setup")
algo_setup = AlgorithmSetup(config_file_path="/home/vixen/rs/dev/marlin_hp/marlin_hp/config.json")

# update user if command line
if (command):
    algo_setup.args['user'] = user
    algo_setup.args['active_bot'] = bot_id
    algo_setup.args['snapshot_id'] = snapshot_id
    


rprint ("Creating Application")
application = SpeciesIdent(algo_setup)

rprint ("Creating world")
application.build_world()
rprint ("World Created")

# --------------------------------------------------------------
# --- Optimisation Data Manager ---                                          |
# --------------------------------------------------------------
# print (application.algo_setup.args)
optimisationDataManager = OptimisationDataManager(application.algo_setup.args['user'], config=application.algo_setup.args,market = application.algo_setup.args['env'], scope=application.algo_setup.args['scope'], user_uid = application.algo_setup.args['user_uid'], optimisation_id=application.algo_setup.args['run_id'])
# print (optimisationDataManager)
optimisationDataManager.defineDescription()
envList = ['live']
optimisationDataManager.setEnv(envList)
optimisationDataManager.dbSendNewOptimisation()

# --------------------------------------------------------------
# --- Data Acq ---                                       |
# --------------------------------------------------------------

# location / snaphsots must be an array or list of locations or ids
location = ['67149847']
#location = ['brixham']
#location = ['netley']
if command:
    location = []
    location.append(location_str)
# --snapshot_ids = []

# Init data adapter (marlin adapter)
data_adapter = None
print (f'Limit {limit} Location {location}')
data_adapter = MarlinData(load_args={'limit' : limit})



    

# data download routine
def download_data():

    # Download data and store locally
    #   -params-
    #   simulation_path : path to save serial data to locally
    #   limit : max number of downlaods
    #   location : location of hydrophone (must be an array)
    #   ss_ids : ids of snapshots
    
    print ("search ids")
    print (sim_ids)
    print ("downloading simulation data")
    data_adapter.download_simulation_snapshots(load_args={'simulation_path':simulation_data_path, 'location':location, 'ss_ids' : sim_ids})
    # print ("downloading signatures")
    # logging.critical('Downloading data')
    # if command == False:
    #     data_adapter.download_signature_snapshots(load_args={'signature_path':signature_data_path,"limit":10})


def load_bot(bot_path):
    file_ptr = open(bot_path, 'rb')
    bot = pickle.load(file_ptr)
    return bot

# data load routine    
def load_data():
    # Load data into the marlin data adapter from a local source
    #   -params-
    #   load_path : path to local rep of serial data
    #   limit : max number of downlaods
    #   snapshot_type : type of snapshot [ simulation | signature ]
   
    global data_adapter
    logging.critical('Loading data')
    #r = data_adapter.load_from_path(load_args={'load_path' : signature_data_path, "snapshot_type":"signature", "limit" : limit})
    r = data_adapter.load_from_path(load_args={'load_path' : simulation_data_path, "snapshot_type":"simulation", 'ss_ids' : sim_ids,"limit" : limit})
    # print (r)
    
data_feed_ = None
data_feed_label = None
def build_feed():
    # Having downloaded and loaded data locally, we can now initialise the data adapter with the data and 
    # feed data to our optimisation framework via our marlin data feed.

    # Build the MARLIN data feed
    global data_feed_
    global data_feed_label
    print ("Initialising data feed.")
    data_feed_ = MarlinDataStreamer()
    data_feed_label = MarlinDataStreamer()
    
    # initilise the simulation datafeeder with downloaded data in data_adapter
    data_feed_.init_data(data_adapter.simulation_data, data_adapter.simulation_index)
    
    data_feed_label.init_data(data_adapter.signature_data, data_adapter.signature_index)


#   ---------------------------------------
#
#   Data Download / Load
#
#   ---------------------------------------

# download_data()

if command == True or len(sim_ids)>0:
    rprint ("Downloading data.")
    #download_data()
    
    load_data()
    
else:
    rprint ("Loading data.")
    
    load_data()
    rprint ("Loading data...Done")



# if command == False:
#     data_adapter.build_game()


print ("sig")
print (data_adapter.signature_index)
print ("sim")
print (data_adapter.simulation_index)




rprint ("Building Data Feed.")
build_feed()
rprint ("Building Data Feed...Done")



#---------------------------------------------------------
#
# Using Derived Data Structures
#
#---------------------------------------------------------
# try:
# data_adapter.build_derived_data(n_fft=application.algo_setup.args['n_fft'])
print ("Derived data for simulation...building")
if data_avail:
    print ("We have data available!")
for snapshot in data_feed_:
    
    s_id = snapshot.meta_data['snapshot_id']
    print (f'Building derived data feed structure {s_id}')
    if not data_avail:
        data_adapter.derived_data = None
        data_adapter.build_derived_data(n_fft=application.algo_setup.args['n_fft'])
        logging.critical(f'Building derived data feed structure {s_id}')
        #snapshot_derived_data = data_adapter.derived_data.build_derived_data(simulation_data=snapshot, sample_delta_t=1.0, f_min = 130000, f_max = 145000)
        snapshot_derived_data = data_adapter.derived_data.build_derived_data(simulation_data=snapshot,  f_min = 130000, f_max = 145000)
        #data_adapter.derived_data.build_band_energy_profile(sample_delta_t=0.01, simulation_data=snapshot,discrete_size = 200)
        data_adapter.derived_data.ft_build_band_energy_profile(sample_delta_t=0.01, simulation_data=snapshot,discrete_size = 300)
        # delta ts must be the same... update code 
        print ("saving ...")
        with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/data/adapters/{s_id}.da', 'wb') as f:  # open a text file
            pickle.dump(data_adapter.derived_data, f) # serialize the list

    else:
        logging.critical(f'Will load derived data for {s_id}')
        

# if data_adapter.derived_data == None:
#     data_adapter.build_derived_data(n_fft=application.algo_setup.args['n_fft'])
        


if not data_avail:
    with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/data/adapters/{s_id}.da', 'wb') as f:  # open a text file
        pickle.dump(data_adapter.derived_data, f) # serialize the list
# except:
#     pass
    # exit for building adapters mode - changhe ss id and location!!! - also download waveform dara, not load -> change f and intx



# when buidling adapter
exit()

# Load saved derived data objects

max_frequency_index = 0

tmp_derived_data = None
if data_avail:
    
    for active_ssid in sim_ids:
    
        with open(f'/home/vixen/rs/dev/marlin_hp/marlin_hp/data/adapters/{active_ssid}.da', 'rb') as f:  # open a text file
            print (f'Building derived data : {active_ssid}')
            data_adapter.derived_data = None
            tmp_derived_data = pickle.load(f) 
            #tmp_derived_data.get_max_f_index()
            data_adapter.derived_data = tmp_derived_data
            #print(tmp_derived_data.fast_index_energy_stats)
            max_frequency_index = 0
            for f_index, value in tmp_derived_data.fast_index_energy_stats.items():
                max_frequency_index = max(f_index, max_frequency_index)
            data_adapter.multiple_derived_data[active_ssid] = tmp_derived_data
            print (f'max frequency index : {max_frequency_index}')
            

for feed in data_feed_:
    print (feed.start_time)
    print (feed.end_time)


# test:
print (f'delta_T : {data_adapter.derived_data.delta_t}')
_f = 130020
_t  = dt.strptime('20140822_125041.000', '%Y%m%d_%H%M%S.%f')
print ('---')
print (_t)
print ('---')
e = data_adapter.derived_data.ft_query_energy_frame(_t, _f)
print ('---')
print (e)
print ('---')
e = data_adapter.derived_data.query_stats_freq_index(0, _t)
print ('---')
print (e)
print ('---')


# num_f = len(data_adapter.derived_data.fast_index_energy_stats)
# print ('---')
# print (f'max index : {num_f}')
# print ('---')
# print (data_adapter.multiple_derived_data)
exit()


# we now have all the active ids


# set simulation data feed
print (f'max e:     {data_adapter.derived_data.max_energy}')
print (f'min e : {data_adapter.derived_data.min_energy}')
print (f'max avg e : {data_adapter.derived_data.max_avg_energy}')


# print (data_adapter.derived_data)
# application.derived_data = data_adapter.derived_data
print ("building xr")
data_adapter.derived_data.build_xr_data(user_uid = "0001vixen")
print ("xr built")

application.derived_data = data_adapter.derived_data
application.multiple_derived_data = data_adapter.multiple_derived_data
application.data_feed = data_feed_

print ("-----")
# print (data_feed_)
# print (application.derived_data.sub_domain_frames)
print ("-----")


# ------------------------------------------------------------------
#
#   Bot(s) download for forward testing
#
# ------------------------------------------------------------------
if command:
    print ("loading bot")
    bot_dir = "/home/vixen/rs/dev/marlin_hp/marlin_hp/bots"
    bot_path = f'{bot_dir}/{bot_id}.vixen'
    print (bot_path)
    bot = load_bot(bot_path)
    application.loaded_bots[bot_id] = bot
    application.mode = 1
    



#------------------------------------------------------------------
#
# World and Data Initialised. Let's play the game.
#
#------------------------------------------------------------------

marlin_game = IdentGame(application, optimisationDataManager)


if application.mode == 0:
    rprint("*** START GAME ***")
    marlin_game.play()
    rprint("*** GAME OVER ***")

if application.mode == 1:
    rprint("*** START BOT ***")
    marlin_game.run_bot()
    

# marlin_game = GameSim(application, optimisationDataManager)
# rprint("*** START GAME ***")
# marlin_game.play()
# rprint("*** GAME OVER ***")
