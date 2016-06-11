# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 01:35:28 2016

Eggs are meant to be broken!

These are example eggs which can be imported and re-used with the wire_egg function
in the application context.  This is great for non-application specific code
that will get re-used across many applications

This promotes a design where non-application specific code is quickly imported 
& wired via passing an egg instance to the context, while application 
specific code is written and wired via annotations

@author: alex
"""

import logging
import inspect

#An egg defines three primary attributes, without which it is not an egg:
#A rank, for instantiation
#A name, for reference in the dict
#A class object, to be returned for instantiation

#The final requirement is that the obj argument must implement both 
#an __init__ and __teardown__ function
class Egg(object):
    
    def __init__(self, rank, name, obj):
        self._rank = rank
        self._name = name
        self._obj = obj
        
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#--------------------------------Logging Egg-----------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------        
        
class Logger(object):

    def __init__(self, context):
        self.log = logging
        self._context = context
        
    def error(self, msg):
        self.log.debug(msg)
        
    def info(self, msg):
        self.log.info(msg)
        
    def debug(self, msg):
        self.log.debug(msg)
        
    def warn(self, msg):
        self.log.warn(msg)
        
    def configure(self, log_file, log_level):
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
        print("Logging configured") 
        
    def __teardown__(self):
        pass
        
class LoggingEgg(Egg):
    
    def __init__(self, rank, name):
        super(LoggingEgg, self).__init__(rank, name, Logger)
        
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#-----------------------------Configuration Egg--------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
    
class ConfigurationManager(object):

    def __init__(self, context):
        self.param_list = {}
        self._context = context

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
                
    def __teardown__(self):
        pass
    
class ConfigurationEgg(Egg):
    
    def __init__(self, rank, name):
        super(ConfigurationEgg, self).__init__(rank, name, ConfigurationManager)
        
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#-------------------------------Utility Egg------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
        
class Utils(object):
    
    def __init__(self, context):
        
        self._context = context
        
        class A(object):
            pass
        
        self._excluded_keys = set(A.__dict__.keys())
                
    #Return a dictionary of class attributes
    def properties_from_class(cls):
        return dict(
            (key, value)
            for (key, value) in cls.__dict__.iteritems()
            if key not in self._excluded_keys and not hasattr(value, '__call__')
            )
            
    #Return a dictionary of class functions
    def functions_from_class(cls):
        return dict(
            (key, value)
            for (key, value) in cls.__dict__.iteritems()
            if key not in self._excluded_keys and hasattr(value, '__call__')
            )
            
    #Return the arguments of a function
    #A named tuple ArgSpec(args, varargs, keywords, defaults) is returned. 
    #args is a list of the argument names. varargs and keywords are the names 
    #of the * and ** arguments or None. defaults is a tuple of default argument 
    #values or None if there are no default arguments; if this tuple has n 
    #elements, they correspond to the last n elements listed in args.
    def arguments_from_function(f):
        return inspect.getargspec(f)
            
    def __teardown__(self):
        pass
            
class UtilEgg(Egg):
    
    def __init__(self, rank, name):
        super(UtilEgg, self).__init__(rank, name, Utils)