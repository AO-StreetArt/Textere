# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 01:42:29 2016

Textere Advanced Example

@author: alex
"""

from Textere import ApplicationContext, autowire, singleton
import sys
import logging

#Start the application context
c = ApplicationContext(ranked_startup=True, use_logging=True)

#Autowire objects such that they will get started automatically when the context is opened
@singleton
@autowire(rank=1, context=c, name="str_factory")
class StringFactory(object):
    
    def __init__(self, context):
        self._counter=0
        self._context = context
        
    def get_str(self):
        return "%s" % (self._counter)
        
    def __teardown__(self):
        self._counter=None
        self._context=None
        
@singleton
@autowire(rank=2, context=c, name="sen_factory")
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
        
        #Open the application context, which builds all the autowired objects
        c.open_context()
        print("Context opened")
        
        #Configure the application using the built-in configuration tool
        c.configure(sys.argv[1])
        logging.debug(c.cm['test'])
        
        #Retrieve the autowired object and use it
        logging.debug(c.eggs["sen_factory"].get_sentance())
        
        #Iterate the counter attribute of the factory
        c.eggs["str_factory"]._counter+=1
        logging.debug(c.eggs["str_factory"]._counter)
           
        c.close_context()
           
        try:
            logging.debug(c.eggs["str_factory"]._counter)
        except Exception as e:
            logging.error("Error getting Egg from Context")
            logging.error(e)
    else:
        print("Wrong number of Input Parameters")
        print("You can execute the script with 'python %s config_file'" % (sys.argv[0]))