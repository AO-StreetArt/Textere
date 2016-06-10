# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 20:23:01 2016

Autowiring of Eggs, Python Equivalent of Java Bean :)
Built for Python2.7

@author: alex
"""

import collections
import logging
import types
import inspect

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#-----------------------------Utility Methods----------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

#Build a list of keys in a blank object to exclude
class A(object):
    pass

_excluded_keys = set(A.__dict__.keys())

#Return a dictionary of class attributes
def properties_from_class(cls):
    return dict(
        (key, value)
        for (key, value) in cls.__dict__.iteritems()
        if key not in _excluded_keys and not hasattr(value, '__call__')
        )
        
#Return a dictionary of class functions
def functions_from_class(cls):
    return dict(
        (key, value)
        for (key, value) in cls.__dict__.iteritems()
        if key not in _excluded_keys and hasattr(value, '__call__')
        )
        
#Return the arguments of a function
#A named tuple ArgSpec(args, varargs, keywords, defaults) is returned. 
#args is a list of the argument names. varargs and keywords are the names 
#of the * and ** arguments or None. defaults is a tuple of default argument 
#values or None if there are no default arguments; if this tuple has n 
#elements, they correspond to the last n elements listed in args.
def arguments_from_function(f):
    return inspect.getargspec(f)
    
class singleton:
    def __init__(self,klass):
        self.klass = klass
        self.instance = None
    def __call__(self,*args,**kwds):
        if self.instance == None:
            self.instance = self.klass(*args,**kwds)
        return self.instance

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#-----------------------Configuration Manager----------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class ConfigurationManager():

    def __init__(self):
        self.param_list = {}

    #Custom Container methods
    def __len__(self):
        return len(self.param_list)

    def __getitem__(self, key):
        return self.param_list[key]

    def __setitem__(self, key, value):
        self.param_list[key] = value

    def __delitem__(self, key):
        del self.param_list[key]

    def __iter__(self):
        return iter(self.param_list)

    def configure(self, config_file):
        #Parse the config file and pull the values
        with open(config_file, 'r') as f:
            for line in f:
                line = line.rstrip() #removes trailing whitespace and '\n' chars
        
                if "=" not in line: continue #skips blanks and comments w/o =
                if line.startswith("#"): continue #skips comments which contain =
        
                k, v = line.split("=", 1)
                self.param_list[k] = v
                
    #Set up the file logging config
    def config_logging(self, log_file, log_level):
        if log_level == 'Debug':
            logging.basicConfig(filename=log_file, level=logging.DEBUG)
        elif log_level == 'Info':
            logging.basicConfig(filename=log_file, level=logging.INFO)
        elif log_level == 'Warning':
            logging.basicConfig(filename=log_file, level=logging.WARNING)
        elif log_level == 'Error':
            logging.basicConfig(filename=log_file, level=logging.ERROR)
        else:
            print("Log level not set to one of the given options, defaulting to debug level")
            logging.basicConfig(filename=log_file, level=logging.DEBUG)
        print("Configuration XML Parsed & Logging configured, for further details on progress please refer to the configured log file") 
        
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#-----------------------Application Context------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------        
     
#We have a global application context with which we register the beans
@singleton
class ApplicationContext():
    
    def __init__(self, ranked_startup=False, use_logging=False):
        
        #Public Attributes
        
        #Configuration Manager
        self.cm = ConfigurationManager()
        
        #Dict of eggs
        self.eggs = {}
        
        #Private Attributes
        
        #Behavioral Parameters
        self._use_logging = use_logging
        self._ranked_startup=ranked_startup
        
        #An unordered dict of ranks & objects
        self._ranked_objects = {}
        self._unranked_objects = {}
        
    #Configure the Application
    def configure(self, config_file):
        print("Entering Configuration")
        self.cm.configure(config_file)
        
        if self._use_logging:
            self.cm.config_logging(self.cm['log_file'], self.cm['log_level'])
        
    #Enter & Exit methods
    def open_context(self):
        
        #We need to start our eggs and add them into our dict
        if self._ranked_startup:
            print("Entering Egg Creation within Context Manager")
            od = collections.OrderedDict(sorted(self._ranked_objects.items()))
            for key, value in od.iteritems():
                obj = value[0]
                name = value[1]
                new_obj = obj(self)
                print("Adding egg to context with name %s" % (name))
                self.eggs[name] = new_obj
        else:
            for key, value in self._unranked_objects.iteritems():
                new_obj = value()
                self.eggs[key] = new_obj
        
    def close_context(self):
        
        #Call the magic cleanup method on all the eggs
        back_items = collections.OrderedDict(reversed(list(self.eggs.items())))
        for key, value in back_items.iteritems():
            print("Shutting down context and ending egg %s" % (key))
            value.__teardown__()
        self.eggs.clear()
        self._ranked_objects.clear()
        self._unranked_objects.clear()

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#-----------------------Autowire Objects---------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class autowire(object):
    
    def __init__(self, rank=0, context=None, name=""):
        self.object = None
        self._rank = rank
        self._context = context
        self._name = name
        
    def __call__(self, obj):
        
        self.object = obj
        if self._context._ranked_startup:
            print('Adding object to Ranked Objects with name %s' % (self._name))
            self._context._ranked_objects[self._rank] = (self.object, self._name)
        else:
            print('Adding object to Unranked Objects with name %s' % (self._name))
            self._context._unranked_objects[self._name] = self.object
        return self.object
        
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#-------------------Generate Getters & Setters---------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
        
class getters(object):
    
    def __init__(self, property_start_character="_"):
        self.prop_start_char = property_start_character
        
    def __call__(self, obj):
        
        for attr in dir(obj):
            
            #Add a Getter for the property and bind it to the object
            if attr[0] == self.prop_start_char:
                pass