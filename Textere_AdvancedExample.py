# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 01:42:29 2016

Textere Advanced Example

@author: alex
"""

import sys

from Textere import ApplicationContext, autowire, singleton, getters, setters
from Eggs import ConfigurationEgg, LoggingEgg

#Start the application context
c = ApplicationContext(ranked_startup=True)

#Register the Logging & Configuration Eggs with the Application Context
cegg = ConfigurationEgg()
legg = LoggingEgg()

c.wire_egg(1, "config", cegg)
c.wire_egg(2, "logging", legg)

#Autowire objects such that they will get started automatically when the context is opened
@getters(property_start_character="_", context=c, name="str_factory")
@setters(property_start_character="_", context=c, name="str_factory")
@autowire(rank=3, context=c, name="str_factory")
@singleton
class StringFactory(object):
    
    def __init__(self, context):
        self._context = context
        self._counter=0
        
    def get_str(self):
        return "%s" % (self._counter)
        
    def __teardown__(self):
        self._counter=None
        self._context=None

@autowire(rank=4, context=c, name="sen_factory")        
@singleton
class SentanceFactory(object):
    
    def __init__(self, context):
        self._context = context
        
    def get_sentance(self):
        return "This is a sentance %s" % (self._context.eggs["str_factory"].get_str())
        
    def __teardown__(self):
        self._context = None
        
#Main Method        
        
if __name__ == "__main__":
    if len(sys.argv) == 2:
        
        logging = c.eggs["logging"]
        
        #Open the application context, which builds all the autowired objects
        c.open_context()
        print("Context opened")
        
        c.eggs["config"].configure(sys.argv[1])
        
        cm = c.eggs["config"]
        
        c.eggs["logging"].configure(cm["log_file"], cm["log_level"])
        
        #Configure the application using the built-in configuration tool
        logging.debug(cm['test'])
        
        fact = c.eggs["str_factory"]
        count = fact.get_counter()
        
        #Retrieve the autowired object and use it
        logging.debug(fact.get_sentance())
        
        #Iterate the counter attribute of the factory
        #c.eggs["str_factory"].set_counter(c.eggs["str_factory"], c.eggs["str_factory"].get_counter(c.eggs["str_factory"])+1)
        fact.set_counter(count+1)
        fact._counter+=1
        #logging.debug(c.eggs["str_factory"].get_counter(c.eggs["str_factory"]))
        logging.debug(fact.get_counter())
           
        c.close_context()
           
        try:
            #logging.debug(c.eggs["str_factory"].get_counter(c.eggs["str_factory"]))
            logging.debug(c.eggs["str_factory"].get_counter())
        except Exception as e:
            logging.error("Error getting Egg from Context")
            logging.error(e)
    else:
        print("Wrong number of Input Parameters")
        print("You can execute the script with 'python %s config_file'" % (sys.argv[0]))