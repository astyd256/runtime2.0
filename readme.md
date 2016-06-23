# VDOM Runtime

## Installation

Download latest runtime
There are two executable files in the sources directory:
* server.py - server executable
* manage.py - auxiliary management utility

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

Where <location> is the location of the application XML file.

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
