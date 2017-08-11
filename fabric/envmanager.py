"""
fabric module that handles groups of images

normally when a group starts it starts a minimal number of servers
"""
from environments import groups
from hostmanager import *
from hostbuilder import *
from deploy import *
import os, random
from fabric.api import execute, settings, env
from fabric.decorators import task, runs_once, hosts

env.warn_only = True

def _deploy_and_test(service, version):
	"""starts a version of a service on env.hosts"""
	execute('{}_deploy'.format(service), version)
	execute('{}_start'.format(service))
	execute('{}_test'.format(service))

@task
@runs_once
@hosts('localhost')
def env_start_all(group):
	"""spins up all hosts in a group and deploys a service to them"""
	if group not in groups: abort("invalid group!")
	# this clears the booted_log so we can see who actually successfully came up
	restart_nginx()
	for image in groups[group]['roles']['workers']:
		image_start(image)
	hosts_reset()
	service = groups[group]['service']
	version = groups[group]['version']
	_deploy_and_test(service, version)

	for image in groups[group]['roles']['loadbalancers']:
		image_start(image)

@task
@runs_once
@hosts('localhost')
def env_start_min(group, pick_randomly=False):
	"""start minimal number of hosts in a group"""
	if group not in groups: abort("invalid group!")

	restart_nginx()

	lblist = groups[group]['roles']['loadbalancers']
	workers = groups[group]['roles']['workers']

	if pick_randomly:
		lblist[random.randint(0,len(lblist))]
		worker = workers[random.randint(0,len(workers))]
	else:
		lb = lblist[0] 
		worker = workers[0] 

	image_start(worker)
	hosts_reset()
	service = groups[group]['service']
	version = groups[group]['version']
	_deploy_and_test(service, version)

	image_start(lb)

@task
@runs_once
@hosts('localhost')
def env_start_worker(image,service,version):
	"""(re)starts a specific worker image and service"""
	image_stop(image)
	image_start(image)
	_deploy_and_test(service, version)
	
@task
@runs_once
@hosts('localhost')
def env_stop(group):
	"""stops all hosts in a group"""
	if group not in groups: abort("invalid group!")
	for image in groups[group]['images']:
		image_stop(image)

