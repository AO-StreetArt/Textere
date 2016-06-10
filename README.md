# What is Textere?

Textere is the latin word for 'Weave Together', and forms the basis for the word 'Context' in modern English.

Textere is a library designed to make Python programming even easier.  It uses some of the same concepts as Spring Technologies, but does not adhere to the implementation or all functionality.  Below is a list of currently supported functionality:

* Fully functional Application Context capable of storing program values
* Auto-Wiring of 'Eggs', a Singleton class that gets a few guarantees
* Annotations for Singletons and Eggs
* Built in properties file reader
* Built in logging module
* Configurable Behavior

Examples can be found in the examples folder.

## Application Context

The Application Context is a container for the application which allows different modules to communicate.  It also allows for auto-wiring.

We declare an application context like so:

`c = ApplicationContext(ranked_startup=True, use_logging=True)`

By default, both parameters are False.  Ranked startup = True has a few guarantees that ranked_startup=False does not, but also requires that every rank is unique (see the autowire annotation below):

* Eggs will be started in order of rank (`__init__()` called)
* Eggs will be cleaned in reverse order of rank (`__teardown__()` called)
* Eggs will be available by name in the context, while the context is open.  For Example:

`c.open_context()`

`print(c.eggs["sen_factory"].get_sentance())`

`c.close_context()`

## Auto-Wiring

'Auto-Wiring' is a concept which is meant to allow faster programming.

We use an annotation (decorator) to mark a class for auto-wiring:

`@singleton`

`@autowire(rank=1, context=c, name="str_factory")`

`class SentanceFactory(object):`

An auto-wired object ('Egg') is loaded into the dict c.eggs when c.open_context() is called, and removed when c.close_context() is called (as well as calling those objects' respective `__teardown__` functions).

Full example code may be found in examples folder.

## Install & Licensing

The library is MIT License and with no dependencies outside of Python2.7 standard libs.  Download & Enjoy!
