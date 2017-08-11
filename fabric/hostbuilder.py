"""
tools for manually building hosts with virtualbox

we only have one type of host we can build from scratch
in reality we need to distinguish between two roles:

- load balancers that accept requests on port 80 and 
- workers that actually handle responding to requests

the latter should add their ip to the BOOTED_LOG (../inventory/booted_log)
so that hostmanager.py can find them and deploy code to them
"""

from fabric.api import local, prompt
from fabric.decorators import runs_once, hosts, task
import time, random

def _confirm_image_op(msg):
	cont = prompt("{} Continue? y/n".format(msg), default='n', validate='^[YyNn]')
	if cont.lower() == 'n':
		print("aborting")
		return False
	return True

@task
@hosts('localhost')
def image_build(image=None,confirm='confirm'):
	"""create a generic host image using virtualbox"""
	if image is None:
		image = prompt('enter image name for new image: ')
	if confirm == 'confirm' and not _confirm_image_op(
			'will try and create new image "{}" this will take a few minutes'.format(image),
		): return
	local('./vbox.sh "{}"'.format(image))

@task
@hosts('localhost')
def image_clone(image=None):
	"""clone an existing image using virtualbox: DO NOT USE"""
	# virtualbox misconfigures clone networking - only have one clone running at a time
	if image is None:
		image = prompt('enter image name for new image: ')
	clone = "{}_{}_clone".format(image,time.time())
	# for some reason we have to keep all mac addresses or the network won't come up
	local('vboxmanage clonevm "{0}" --options keepallmacs --name "{1}" --register'.format(image,clone))

@task
@hosts('localhost')
def image_list():
	"""list all available virtualbox images"""
	images = local('vboxmanage list vms')
	print images

@task
@hosts('localhost')
def image_del(image=None, confirm='confirm'):
	"""manually delete a specific image"""
	if image is None:
		image = prompt('enter image name to delete: ')
	if confirm == 'confirm' and not _confirm_image_op('will permanently delete image "{}".'.format(image)):
		return
	local('vboxmanage unregistervm "{}" --delete'.format(image))

@task
@hosts('localhost')
def image_start(image=None):
	"""manually start a specific image"""
	if image is None:
		image = prompt('enter image to start: ')
	local('vboxmanage startvm "{}" --type headless &'.format(image))

@task
@hosts('localhost')
def image_stop(image=None):
	"""manually stop a specific image"""
	if image is None:
		image = prompt('enter image to stop: ')
	local('vboxmanage controlvm "{}" poweroff'.format(image))

