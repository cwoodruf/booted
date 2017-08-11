#!/usr/bin/env python
import getpass
from fabric.api import prompt, env
try:
	import credentials
except:
	env.user = prompt("user name: ")
	env.password = getpass.getpass("password: ")
	
from envmanager import *
from hostbuilder import *
from hostmanager import *
from deploy import *

