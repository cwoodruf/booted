"""
infrastructure code for servers
servers can be discovered via the inventory/booted_log
which they should automatically update when they start

there are two classes of servers:
regular servers that run services
load balancers that farm work out to the regular servers
"""
try:
	import hosts
except:
	print "Missing hosts list run 'hosts_filter' goal to generate one"

from fabric.api import env, sudo, put, get, run, local, hide, prompt, abort
from fabric.decorators import task, hosts, runs_once
from fabric.context_managers import settings
import re, os

# should be in ../inventory/booted_log from here
DEF_BOOTED_LOG=os.environ['BOOTED_LOG']

@task
@runs_once
@hosts('localhost')
def hosts_reset():
	"""do a hard reset of env.hosts"""
	hosts_clear(False)
	hosts_filter()

@task
@runs_once
@hosts('localhost')
def hosts_clear(confirm=True):
	"""clear the current env.hosts list"""
	if confirm:
		ret = prompt("This will delete the hosts list. Continue? y/n", 
				default='n', validate='^[NnYy]')
	if not confirm or ret.lower() == 'y':
		with settings(warn_only=True):
			local("rm hosts.py*")
	else:
		print("no change")

@task
@runs_once
@hosts('localhost')
def hosts_list():
	"""list current hosts"""
	print(env.hosts)

@task
@runs_once
@hosts('localhost')
def hosts_logged(booted_log=DEF_BOOTED_LOG, save_hosts=True):
	"""get all hosts in booted_log"""
	hosts = {}
	with open(booted_log, "r") as log:
		for logline in log:
			hostline = re.search(r'((\d{1,3})(?:\.\d{1,3}){3}).*', logline)
			if hostline is None or hostline.group(2) == '127' or hostline.group(1) == os.environ['LOCALHOST']:
				continue
			host = hostline.group(1)
			hosts[host] = True

	for host in env.hosts:
		hosts[host] = True
	if len(hosts.keys()) > 0 and save_hosts:
		print(hosts)
		_save_env_hosts(hosts)
	return hosts

@task
@runs_once
@hosts('localhost')
def hosts_filter(booted_log=DEF_BOOTED_LOG):
	"""get contactable hosts using ping"""
	hosts = hosts_logged(booted_log, save_hosts=False)
	for host in hosts:
		with settings(hide('stdout','stderr','running','warnings'),warn_only=True):
			hosts[host] = local("ping -q -w1 -c1 {}".format(host)).succeeded

	if len(hosts.keys()) > 0: 
		print(hosts)
		print("saving hosts")
		_save_env_hosts(hosts)
	else:
		print("no hosts found")

@task
@runs_once
@hosts('localhost')
def restart_nginx(booted_log=DEF_BOOTED_LOG):
	"""restart local nginx and make a new booted log file"""
	with settings(hide('stdout','running')):
		local("mv '{0}' '{0}'.`/bin/date +%Y%m%d_%H%M%S`".format(booted_log))
		local("touch '{}'".format(booted_log))
		local("chmod a+w '{}'".format(booted_log))
		local("sudo service nginx restart")

def _save_env_hosts(hosts):
	"""takes a dict of host ips with T/F and saves them to hosts.py"""
	livehosts = []
	for host in hosts:
		if not hosts[host]:
			continue
		livehosts.append(host)
	with open("hosts.py", "w") as hostf:
		hostf.write("from fabric.api import env\n")
		hostf.write("env.hosts = " + repr(livehosts) + "\n")

