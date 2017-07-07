# VDOM Runtime

## Installation

The first is needed to check that system meets all requirements:

* ply (pip install ply)
* pillow (pip install pillow)
* pycrypto (pip install pycrypto)
* sqlite (pip install pysqlite; copy dll for windows)
* sqlitebck (copy dll for windows)
* xapian (copy module for windows)
* xappy (copy module for windows)
* python-ldap (pip install python-ldap)
* soappy (pip install soappy)

Then download latest runtime. After that must be performed deploy action:

    python manage.py deploy

This action creates required directories and install all types from repository directory.

## Quick start

There are two executable files in the sources directory:

* server.py - main runtime server executable
* manage.py - auxiliary management utility

To install and select application you can use manage.py utility:

    python manage.py install <application XML file location>
    python manage.py select <application uuid or name>

For more detailed information see below.

## Starting runtime server

To start server just type:

    python server.py

Configuration can be found in the settings.py file, also server supports several command line arguments:

* -l, --listen - specify address to listen
* -p, --port - specify port
* -a, --applicaiton - specify application to serve
* -c, --configure - specify filename to load settings
* --preload - preload default application
* --profile - enable profiling

### Override settings

Command line:

    python server.py -c settings.ini

File contents:

    SERVER-ADDRESS = "gerg"
    SERVER-PORT = 4234

## Using manage utility

This utility can be used to perform several maintenance tasks, for example:

* install or uninstall application
* select default application
* list available applications and types
* query internal state from server
* show last stored profile

To perform action utility can be called from the command line as follow:

    python manage.py <action> <arguments>...

Or can work in interactive mode - just lunch manage.py without arguments.

### Install application or type

Action:

    install <location>

Example:

    install x:\data\promail.xml

Where *location* is the location of the application XML file.

### Uninstall application or type

Action:

    uninstall <application or type name or uuid>

Example:

    uninstall promail

### Select default application

Action:

    select <application name or uuid>

Example:

    select promail

### List available applications and types

Action:

    list

### View log

Display actual server log and update it in the realtime.

Action:

    log

### Show application or type details

Show some information about available application or type like id, name, attributes and so on.

Action:

    show <application or type name or uuid>

Example:

    show form

## Debugging and profiling

Manage utility also have several actions to help with debugging and profiling.

### Show object statistics

This action require enabled watcher.

Action:

    watch analyze objects

Example:

    watch analyze objects --sort counter --lim 75

This command show 75 most common object types sorted by count.

### Show profiling statistics

This command require enabled profiler.

Action:

    profile show
    profile show tasks

### Drop profiling statistics

This command require enabled profiler.

Action:

    profile drop
    profile drop tasks

### Query profiling statistics

This command require enabled profiler.

Action:

    watch query profile c:\temp
    watch query profile c:\temp tasks

### Query profiling callgraph

This command require enabled profiler.

Action:

    watch query callgraph c:\temp
    watch query callgraph c:\temp tasks
