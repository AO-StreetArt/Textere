# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 22:08:21 2016

Textere Example

@author: alex
"""

from Textere import ApplicationContext, autowire
from Eggs import ConfigurationEgg
import sys

#Start the application context
c = ApplicationContext(ranked_startup=True)

#Import and wire in the configuration Egg
config = ConfigurationEgg(rank=1, name="configuration")
c.wire_egg(config)

#Autowire an object such that it will get started automatically when the context is opened
@autowire(rank=2, context=c, name="str_factory")
class StringFactory(object):
    
    def __init__(self, context):
        self.counter=0
        
    def get_str(self):
        return "%s" % (self.counter)
        
    def __teardown__(self):
        self.counter=0
        
if __name__ == "__main__":
    if len(sys.argv) == 2:
        
        #Open the application context, which builds all the autowired objects
        c.open_context()
        print("Context opened")
        
        #Configure the application using the built-in configuration tool
        c.eggs["configuration"].configure(sys.argv[1])
        print(c.eggs["configuration"]['test'])
        
        #Retrieve the autowired object and use it
        print(c.eggs["str_factory"].get_str())
        
        #Iterate the counter attribute of the factory
        c.eggs["str_factory"].counter+=1
        print(c.eggs["str_factory"].counter)
           
        c.close_context()
           
        #Will throw an error as the context is closed
        #print(c.eggs["str_factory"].counter)
    else:
        print("Wrong number of Input Parameters")
        print("You can execute the script with 'python %s config_file'" % (sys.argv[0]))