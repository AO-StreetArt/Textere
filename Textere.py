# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 20:23:01 2016

Autowiring of Eggs, Python Equivalent of Java Bean :)
Built for Python2.7

@author: alex
"""

import collections
import types
import inspect
import new

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
#-----------------------Application Context------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------        
     
#We have a global application context with which we register the beans
@singleton
class ApplicationContext():
    
    def __init__(self, ranked_startup=False):
        
        #Public Attributes
        
        #Dict of eggs
        self.eggs = {}
        
        #Private Attributes
        
        #Behavioral Parameters
        self._ranked_startup=ranked_startup
        
        #Autowire Lists
        
        #An unordered dict of ranks & objects
        self._ranked_objects = {}
        self._unranked_objects = {}
        
        #Getter & Setter Lists
        self._getter_list = []
        self._setter_list = []
        
    #Enter & Exit methods
    def open_context(self):
        
        #Start our eggs and add them into our dict
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
                
        #Generate Getters & Setters for eggs
        for pair in self._getter_list:
            prop_start_char=pair[0]
            name=pair[1]
            obj=pair[2]
            for attr in dir(self.eggs[name]):
            
                print("Testing Attribute %s" % (attr))
                
                #Add a Getter for the property and bind it to the object
                if attr[0] == prop_start_char and attr not in _excluded_keys and attr[:2]!="__":
                    
                    print("Attribute starts with correct character")
                    
                    attr_name = attr[1:]
                    
                    #Here we define a set of symbols within an exec statement and put them into the dictionary d
                    d = {}
                    exec "def get_%s(self): return self.%s" % (attr_name, attr) in d
                    print("Function object defined in d: %s" % (d['get_%s' % (attr_name)]))
                    
                    #Now, we bind the get method stored in d['get_%s'] to our object (class)
                    #types.MethodType( d['get_%s' % (attr_name)], self.eggs[name] )
                    func = d['get_%s' % (attr_name)].__get__(d['get_%s' % (attr_name)], obj)
                    setattr(self.eggs[name], func.__name__, func)
                    #new.instancemethod(d['get_%s' % (attr_name)], self.eggs[name], self.eggs[name].__class__)
                    print("Getter bound to object %s" % (self.eggs[name]))
                    
        for pair in self._setter_list:
            prop_start_char=pair[0]
            name=pair[1]
            obj=pair[2]
            for attr in dir(self.eggs[name]):
                
            
                print("Testing Attribute %s" % (attr))
                
                #Add a Getter for the property and bind it to the object
                if attr[0] == prop_start_char and attr not in _excluded_keys and attr[:2]!="__":
                    
                    print("Attribute starts with correct character")
                    
                    attr_name = attr[1:]
                    
                    #Here we define a set of symbols within an exec statement and put them into the dictionary d
                    d = {}
                    exec "def set_%s(self, new_val): self.%s = new_val" % (attr_name, attr) in d
                    print("Function object defined in d: %s" % (d['set_%s' % (attr_name)]))
                    
                    #Now, we bind the get method stored in d['get_%s'] to our object (class)
                    #types.MethodType( d['get_%s' % (attr_name)], self.eggs[name] )
                    func = d['set_%s' % (attr_name)].__get__(d['set_%s' % (attr_name)], obj)
                    setattr(self.eggs[name], func.__name__, func)
                    print("Setter bound to object %s" % (self.eggs[name]))
        
    def close_context(self):
        
        #Call the magic cleanup method on all the eggs
        back_items = collections.OrderedDict(reversed(list(self.eggs.items())))
        for key, value in back_items.iteritems():
            print("Shutting down context and ending egg %s" % (key))
            value.__teardown__()
        self.eggs.clear()
        self._ranked_objects.clear()
        self._unranked_objects.clear()

    #Serve as a replacement for the annotation to wire imported eggs        
    def wire_egg(self, egg):
        if self._ranked_startup:
            print('Adding object to Ranked Objects with name %s' % (egg._name))
            self._ranked_objects[egg._rank] = (egg._obj, egg._name)
        else:
            print('Adding object to Unranked Objects with name %s' % (egg._name))
            self._unranked_objects[egg._name] = egg._obj

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
    
    def __init__(self, property_start_character="_", context=None, name=""):
        self.prop_start_char = property_start_character
        self._context = context
        self._name=name
        print('Getters initialized with property start character %s' % (self.prop_start_char))
        
    def __call__(self, obj):
        
        self._context._getter_list.append((self.prop_start_char, self._name, obj))
        return obj
        
class setters(object):
    
    def __init__(self, property_start_character="_", context=None, name=""):
        self.prop_start_char = property_start_character
        self._context = context
        self._name=name
        print('Setters initialized with property start character %s' % (self.prop_start_char))
        
    def __call__(self, obj):
        
        self._context._setter_list.append((self.prop_start_char, self._name, obj))
        return obj