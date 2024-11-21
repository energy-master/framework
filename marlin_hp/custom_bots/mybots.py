"""

My Custom Bot - Simple tutorial example

"""
from marlin_brahma.bots.bot_root import *
import random



version = 1.0
print (f"Acoustic Bot [{version}]")



class testBot(object):
    def __init__(self):
        print ("Test Bot")


class AcousticBot(BotRoot):
    
    def __init__(self, myenv="", myspecies = "acoustic_bot", myargs=None, version="1_0_0"):
        super().__init__(myenv=myenv, myspecies = myspecies, myargs=myargs, version=version)


        
    def save(self, save_folder=""):
        
        import pickle
        print ("saving myself")
        print (save_folder)
        try:
            fileName = save_folder + self.name + '.vixen'
            saveFile = open(fileName, 'wb')
            pickle.dump(self, saveFile)
            saveFile.close()
        except Exception as e:
            print (e)
            
    # def __str__(self):
    #     return (f'trade bot: {self.name}')
        


