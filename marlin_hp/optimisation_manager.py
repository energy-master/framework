
import random
import errno
import os, sys
import time
import datetime

import requests
import json
import pickle

import base64

# sys.path.insert(0, '/home/vixen/.local/lib/python3.8/site-packages')
print (sys.path)

import mysql.connector


#import logging


# from brahmaAppConf import *

class OptimisationDataManager(object):

  def __init__(self, user = "", config = None, market = "", scope="", user_uid="", optimisation_id=""):
    
    
    #owner of optmisation run
    self.user = user
    self.user_uid = user_uid
    self.scope = scope
    #optmisation id
    
    self.optimsationID = user + str(random.randint(1,100000))
    self.optimsationID = optimisation_id
    #config file
    self.config = config
    self.market = market
    
    self.snap = str(datetime.datetime.now())
    
    self.status = 1
    self.op_description = None


  def defineDescription(self):
    '''Build and save optimisation desctriptions file
    '''

    self.op_description = {
        "user"  : self.user,
        "id"    : self.optimsationID,
        "date"  : self.snap,
        "market": self.market,
        "config": self.config
    }

    print (self.op_description)


  def getDescription(self):
    import json
    return json.dumps(self.op_description)

  def buildRemoteStructure(self):
    '''Create directory structure required for remote server.
    '''
    from ftplib import FTP
    ftp = FTP('ftp.vixencapital.com')
    ftp.login(user='vixencapital.com', passwd='Edinburgh69!')

    #go to roor directory of optimisation
    ftp.cwd('opdata')

    opRootFolder = self.optimsationID

    try:
      ftp.cwd(opRootFolder)
    except:
      print (opRootFolder)
      ftp.mkd(opRootFolder)
      ftp.mkd(opRootFolder + "/bots")
      ftp.mkd(opRootFolder + "/tracker")
      ftp.mkd(opRootFolder + "/tracker/gen")

  def createGenFolder(self, gen = 0):
    '''Create generation data folder on remote server

    Keyword Arguments:
        gen {int} -- [description] (default: {0})
    '''
    from ftplib import FTP
    ftp = FTP('ftp.vixencapital.com')
    ftp.login(user='vixencapital.com', passwd='Edinburgh69!')

    ftp.cwd('opdata/' + self.optimsationID + "/tracker/gen")
    genFolder =  str(gen)

    try:
      ftp.cwd(genFolder)
    except:
      ftp.mkd(genFolder)



  def createFileStructures(self):
    '''
    Create folders and files requried for optimisation
    '''
    newOptimisationPath = OP_OUTPUT_FOLDER + str(self.optimsationID)
    print (newOptimisationPath)
    
    #os.chdir(newOptimisationPath)

    #print (os.getcwd())
    try:
      directoryPATH = os.path.join(OP_OUTPUT_FOLDER, str(self.optimsationID))
      trackerPATH = os.path.join(directoryPATH, "tracker")
      botsPATH = os.path.join(directoryPATH, "bots")
      #print (directoryPATH)
      os.mkdir(directoryPATH)
      os.mkdir(trackerPATH)
      os.mkdir(botsPATH)
    except OSError as e:
      if e.errno != errno.EEXIST:
        raise
        


  def setEnv(self, dates = []):
    self.dates = dates
    self.op_description['dates'] = self.dates

  def uploadFileStructures(self):
    '''Upload required files to vixen server in order to visualise optimisation progress...
    '''
    pass


  def saveDescription(self):
    '''Save description to file
    '''
    directoryPATH = os.path.join(OP_OUTPUT_FOLDER, str(self.optimsationID))
    pathToFile = directoryPATH + "/optimisation_desc.json"
    print (pathToFile)
    
    content = self.getDescription()
    
    f = open(pathToFile, "w")
    #--f.write(content)
    f.close()
    

  def recordBotStructures(self, generation = 0, content = "", botName = ""):
    """Record bot strutures every generation.


    Keyword Arguments:
        generaion {int} -- [description] (default: {0})
        content {str} -- [description] (default: {""})

    """

    dataSend = {}
    dataSend["optimisation_id"] = self.optimsationID
    dataSend["generation"] = generation
    dataSend["bot_name"] = botName
    dataSend["action"] = "update_structure"
    dataSend["structure"] = content

    dataSendJSON = json.dumps(dataSend)

    print ("sending trader structure data")
    print (dataSendJSON)

    

    API_ENDPOINT = "https://www.vixencapital.com/api/optimisation/index.php"
    try:
      r = requests.post(url = API_ENDPOINT, json = dataSendJSON)
      response = r.text
      print("Str Sent")
      print(r.status)
      
    except:
      print ("error sending")
   
    
  def recordBot(self, botName = "", binaryImg=""):
    '''
        Save bot to db
    '''
    # directoryPATH = os.path.join(OP_OUTPUT_FOLDER, str(self.optimsationID))
    # imagePATH = os.path.join(directoryPATH, "tracker", "gen" , str(generation), "" )

    # imageFile = imagePATH + botName + ".png"

    # with open(imageFile, 'rb') as file:
    #   binaryImgData = file.read()

    import base64
    encodestring = base64.b64encode(binaryImg)

    dataSend = {}
    dataSend["optimisation_id"] = self.optimsationID
    dataSend["market"] = self.market
    dataSend["bot_name"] = botName
    dataSend["action"] = "saveBot"
    dataSend["botimage"] = encodestring

    API_ENDPOINT = "https://www.vixencapital.com/api/optimisation/img/"
    try:
      r = requests.post(url = API_ENDPOINT, data = dataSend)
    except:
        
      print("request error")
    #print(r)

    response = r.text
    #print (response)

  def recordBotImage(self, generation=0, botName = ""):
    '''
        Update structure image for bot on DB
    '''
    directoryPATH = os.path.join(OP_OUTPUT_FOLDER, str(self.optimsationID))
    imagePATH = os.path.join(directoryPATH, "tracker", "gen" , str(generation), "" )

    imageFile = imagePATH + botName + ".png"

    with open(imageFile, 'rb') as file:
      binaryImgData = file.read()

    import base64
    encodestring = base64.b64encode(binaryImgData)

    dataSend = {}
    dataSend["optimisation_id"] = self.optimsationID
    dataSend["generation"] = generation
    dataSend["bot_name"] = botName
    dataSend["action"] = "submit_image"
    dataSend["image"] = encodestring

    API_ENDPOINT = "https://www.vixencapital.com/api/optimisation/img/"
    try:
      r = requests.post(url = API_ENDPOINT, data = dataSend)
    except:
        
      print("request error")
    #print(r)

    response = r.text
    #print (response)


  def saveBotDecisions(self, generation = 0, content = "", botName = ""):
    #create directory for generation
    mainPath = os.path.join(OP_OUTPUT_FOLDER, str(self.optimsationID), "tracker", "gen", str(generation))
    if os.path.isdir(mainPath)==False:
      os.makedirs(mainPath)
    #generation folder

    #write file
    pathToFile = mainPath + "/" + botName +"_dec.json"
    f = open(pathToFile, "w")
    #--f.write(content)
    f.close()


  def recordBotDecisions(self, generation = 0, content = "", botName = ""):
    """Record bot decisions taken at every generation.


    Keyword Arguments:
        generaion {int} -- [description] (default: {0})
        content {str} -- [description] (default: {""})

    """
  
    dataSend = {}
    dataSend["optimisation_id"] = self.optimsationID
    dataSend["generation"] = generation
    dataSend["bot_name"] = botName
    dataSend["action"] = "update_decisions"
    dataSend["decisions"] = json.dumps(content)

    dataSendJSON = json.dumps(dataSend)

    #print ("sending trader decision data")
    

    API_ENDPOINT = "https://www.vixencapital.com/api/optimisation/index.php"
    try:
      r = requests.post(url = API_ENDPOINT, data = dataSendJSON)
    except:
      print ("request error")
    response = r.text
    #print (response)


  def recordFitnessValues(self, generation = 0, content = "",structure = ""):
    """Record inter optimisation run (per generation) trader fitness values
    to db for record keeping

    Keyword Arguments:
        generation {int} -- [description] (default: {0})
        content {json encoded object} -- [description] (default: {""})
    """

    print ("updating fitness vals gen:{0}".format(generation))
    dataSend = {}
    dataSend["optimisation_id"] = self.optimsationID
    dataSend["generation"] = generation
    dataSend["action"] = "update_optimisation"
    dataSend["performance_data"] = content
    #dataSend["structures"] = structure

    dataSendJSON = json.dumps(dataSend)
    #print (dataSendJSON)

    API_ENDPOINT = "https://www.vixencapital.com/api/optimisation/index.php"
    try:
      r = requests.post(url = API_ENDPOINT, data = dataSendJSON)
    except:
      print("request error")
    response = r.text
    #print (response)

  def closeOptimisationRecord(self):

    dataSend = {}
    dataSend["status"] = self.status
    dataSend["optimisation_id"] = self.optimsationID
    dataSend["action"] = "close_optimisation"
    dataSendJSON = json.dumps(dataSend)


    API_ENDPOINT = "https://www.vixencapital.com/api/optimisation/index.php"
    try:
      r = requests.post(url = API_ENDPOINT, data = dataSendJSON)
    except:
      print("request error")
    response = r.text

  def saveFitnessValues(self, generation = 0, content = ""):
    '''
      Save fitness values of all bots in game
    '''

    #create directory for generation
    mainPath = os.path.join(OP_OUTPUT_FOLDER, str(self.optimsationID), "tracker", "gen", str(generation))
    if os.path.isdir(mainPath)==False:
      os.makedirs(mainPath)
    #generation folder

    #write file
    pathToFile = mainPath + "/fitness.json"
    f = open(pathToFile, "w")
    #--f.write(content)
    f.close()


  def saveRankings(self, generation = 0, content = ""):
    '''Bot rankings. This may be done server side rather than saving here. Evolution class deals with ranking.

    Keyword Arguments:
        generation {int} -- [description] (default: {0})
        content {str} -- [description] (default: {""})
    '''

      #create directory for generation
    mainPath = os.path.join(OP_OUTPUT_FOLDER, str(self.optimsationID), "tracker", "gen", str(generation))
    os.makedirs(mainPath)
    #generation folder

    #write file
    pathToFile = mainPath + "/rankings.json"
    f = open(pathToFile, "w")
    #--f.write(content)
    f.close()

  def uploadPreData(self):
    '''
    Upload data before optmisation run
    '''
    mainPath = os.path.join(OP_OUTPUT_FOLDER, str(self.optimsationID), "")
    filenameLocal = mainPath + "optimisation_desc.json"
    filenameSrve = "optimisation_desc.json"

  def UploadPostData(self):
    '''Upload any data required after optimisation (e.g. time taken, final bot list )
    '''

  def UploadRunData(self):
    '''upload data generated during optimisation (e.g. fitness)
    '''


  def saveBotStructure(self, bot = None):
    '''Save the bot structure definition

    Keyword Arguments:
        bot {[trader_template]} -- [description] (default: {None})
    '''

  def saveDecisions(self, botName = "" , decisionList = None):
    '''Save bot decisions for visualisation later

    Keyword Arguments:
        botName {str} -- [description] (default: {""})
        decisionList {[type]} -- [description] (default: {None})
    '''
    pass


  

  def dbSendNewOptimisation(self):
    """Send new optisation run data to db for records.
        data = json.dumps(data) # object -> string
            API_ENDPOINT = "https://www.vixencapital.com/api/tradebook/closedtrades/"
            r = requests.post(url = API_ENDPOINT, data = data)
            response = r.text
            print (response)
    """
    dataSend = {}
    dataSend["user_uid"] = self.user_uid
    dataSend["market"] = self.market
    dataSend["desc"] = self.getDescription()
    dataSend["optimisation_id"] = self.optimsationID
    dataSend["num_gen"] = self.config['number_generations']
    dataSend["action"] = "newOp"


    dataSendJSON = json.dumps(dataSend)
    # print (dataSendJSON)
 

    API_ENDPOINT = "https://www.vixencapital.com/api/optimisation/"
    #requests.post(url=API_ENDPOINT, data = {'test' : 'test'})
    try:
      r = requests.post(url = API_ENDPOINT, data = dataSendJSON)
      print(r.status_code)
    except:
      print ("request error")

    #response = r.text
    # print ("New Op Response Code:")
    
    

  def closeRun(self, numberBirths=0):
    """Close optimisation run and add to db for records
    """
    dataSend = {}
    dataSend["status"] = self.status
    dataSend["optimisation_id"] = self.optimsationID
    dataSend["number_births"] = numberBirths
    dataSend["action"] = "close_optimisation"
    dataSendJSON = json.dumps(dataSend)

    #print (dataSendJSON)
    API_ENDPOINT = "https://www.vixencapital.com/api/optimisation/"
    try:
      r = requests.post(url = API_ENDPOINT, data = dataSendJSON)
    except:
      print("request error")
    response = r.text
    #print (response)

  def setStatus(self, status = 0):
    """Update optimisation status locally and remotely

    Keyword Arguments:
        status {int} -- [description] (default: {0})
    """

    #local update
    self.status = status

    #db update





  def saveWinningBots(self, botlist, species, final = False):
    """Pass winning bot list and species

    Arguments:
        botlist {[type]} -- [description]
        species {[type]} -- [description]
    """
    if final == False:
      for botID in botlist:
        rnd_bot = species[botID]
        rnd_bot.name = botID + str(random.randint(1,100000))
        #self.saveBot(species[botID])
        self.saveBot(rnd_bot)
        self.recordWinningBot(rnd_bot)
      return 
        
    if final == True:
      for botID in botlist:
        #rnd_bot = species[botID]
        #rnd_bot.Name = botID + str(random.randint(1,100000))
        #self.saveBot(species[botID])
        if botID in species:
          print ("ind save - op manager")
          print (species[botID])
          bot = species[botID]
          #bot.name = bot.name + str(random.randint(1,100000))
          self.saveBot(bot)
        else:
          print ("Individual not found for saving")
      return 

        

  def recordWinningBot(self, bot):
    """Record optimisation winners to db


    Arguments:
        botlist {[type]} -- [description]
    """
    #logger.info('Winning bots recorded')
    botStr = bot
    botID = bot.name
    #--build data for posting
    dataSend = {}
    dataSend["action"] = "record_bot"
    dataSend["user"] = self.user_uid
    dataSend["botID"] = botID
    dataSend["botStructure"] = botStr.printStr()
    dataSend["market"] = self.market
    dataSend["direction"] = botStr.direction
    dataSend["optimisationID"] = self.optimsationID
    dataSend["parent"] = botStr.parent
    dataSend["scope"] = self.scope
    #.info('Wining bots recorded: %s', botID)
    dataSendJSON = json.dumps(dataSend)
    #print (dataSendJSON)


    #--post data
    try:
      API_ENDPOINT = "https://www.vixencapital.com/api/optimisation/"
      try:
        r = requests.post(url = API_ENDPOINT, data = dataSendJSON)
        response = r.text
      except:
        print("request error")

    except:
      #logger.critical('Error recording winning bot')
      pass


    #print (response)


  def recordWinningBots(self, botlist, species):
    """Record optimisation winners to db


    Arguments:
        botlist {[type]} -- [description]
    """
    print ("sending structures")
    #logger.info('Winning bots recorded')
    for botID in botlist:
      if botID not in species:
        continue
            
      #--build data for posting
      dataSend = {}
      dataSend["action"] = "record_bot"
      dataSend["user"] = self.user_uid
      dataSend["botID"] = botID
      dataSend["botStructure"] = species[botID].printStr()
      dataSend["market"] = self.market
      dataSend["direction"] = species[botID].direction
      dataSend["optimisationID"] = self.optimsationID
      dataSend["parent"] = species[botID].parent
      dataSend["scope"] = self.scope
      
      #logger.info('Wining bots recorded: %s', botID)
      dataSendJSON = json.dumps(dataSend)
      # print (dataSendJSON)


      #--post data
      try:
        API_ENDPOINT = "https://www.vixencapital.com/api/optimisation/"
        try:
          r = requests.post(url = API_ENDPOINT, data = dataSendJSON)
          response = r.text
          print("Structure response code:")
          print(r.ok)
        except:
          print("request post error")
        

      except:
        #logger.critical('Error recording winning bot')
        pass
      
      #save binary bot
      
      
      bot_serial = pickle.dumps(species[botID])
      bot_e_serial = base64.b64encode(bot_serial)
      
      
      # binary_data = {}
      # binary_data["bot_name"] = botID
      # binary_data["image_binary_string"] = bot_e_serial
      # # print (bot_serial)
      # print ("asfsf 2")
      # b_data_send = json.dumps(binary_data)
      
      try:
        API_ENDPOINT = f"https://vixen.hopto.org/veta/api/v1/platform/trader/save/index.php?botID={botID}&file={bot_e_serial}" 
        print (API_ENDPOINT)
        
        try:
          r = requests.get(url = API_ENDPOINT)
          response = r.text
          print("Structure binary response code:")
          print(r.ok)
        except:
          print("request post error")
        

      except:
        logger.critical('Error recording winning bot')
        print ("Image save error")


  def saveBot(self, bot = None):
    '''Serialise and save bot to file. This is done for winning bots in optimisations

    Keyword Arguments:
        bot {[type]} -- [description] (default: {None})
    '''

    BOT_SAVE_FOLDER = "bots/"
    #serialise bot to local file.
    bot.save(save_folder=BOT_SAVE_FOLDER)
    
    
    
    
    




  def dbConnect(self):

    self.mydb = mysql.connector.connect(
        host="localhost",
        user="yourusername",
        passwd="yourpassword"
    )


  def dbDisconnect(self):
      pass





if __name__ == "__main__":
  print ("running")
  # om = OptimisationDataManager("global", config = OptimisationParameters , market = "eurusd")
  # om.createFileStructures()
  # om.saveDescription()
  dataSend = {}
  dataSend["action"] = "record_bot"
  dataSend["user"] = '54353534_uid'
  dataSend["botID"] = '535353453'
  dataSend["botStructure"] = '5353534fdfdfdf'
  dataSend["market"] = 'eur'
  dataSend["direction"] = 1
  dataSend["optimisationID"] = 'fsdfs'
  dataSend["parent"] = 'eden'
  dataSend["scope"] = 'global'
  
  #logger.info('Wining bots recorded: %s', botID)
  dataSendJSON = json.dumps(dataSend)
  print (dataSendJSON)


  #--post data
  try:
    API_ENDPOINT = "https://www.vixencapital.com/api/optimisation/"
    try:
      r = requests.post(url = API_ENDPOINT, data = dataSendJSON)
      response = r.text
      print("Structure response code:")
      print(r.ok)
    except:
      print("request post error")
    

  except:
    #logger.critical('Error recording winning bot')
    pass





  
