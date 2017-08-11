from fabric.api import env
import os
env.user = os.environ['BOOTED_USER']
env.password = os.environ['BOOTED_PW']

