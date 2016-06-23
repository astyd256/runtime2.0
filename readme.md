# VDOM Runtime

## Installation

Check you system to meet all requirements:

* ply (pip install ply)
* pillow (pip install pillow)
* pycrypto (pip install pycrypto)
* sqlite (pip install pysqlite; copy dll for windows)
* sqlitebck (copy dll for windows)
* xapian (copy module for windows)
* xappy (copy module for windows)
* python-ldap (pip install python-ldap)
* soappy (pip install soappy)

Download latest runtime. Under Linux-like system may be needed to update settings.py then create required directories and move resources and other files according this settings.

There are two executable files in the sources directory:

* server.py - server executable
* manage.py - auxiliary management utility

To install and select application you must execute command:

    python manage.py install <location>
    python manage.py select <uuid>

More detailed information for actions see below.

## Server

To start server just type:

    python server.py

Configuration are taken from settings.py file, also server supports several command line arguments:
* -l, --listen - specify address to listen
* -p, --port - specify port
* -a, --applicaiton - specify application to serve

## Manage

This utility can be used to perform several maintenance tasks, for example:
* install/uninstall application
* select default application
* show installed applications and types
Utility can be used from command line as follow:

    python manage.py <action> <arguments>...

Also can work in interactive mode - just lunch manage.py without arguments.
    
### Install application

Action:

    install <location>
    install x:\data\promail.xml

Where "location" is the location of the application XML file.

### Uninstall application

Action:

    uninstall <application name or uuid>
    uninstall promail

### Select default application

Action:

    select <application name or uuid>
    select promail

### Show available applications and types

Action:

    show
