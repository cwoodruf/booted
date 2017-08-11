"""
infrastructure code for deploying versions of applications to servers
- versions of the code are assumed to be known before hand
- we are assuming for now that all services go on all servers 
  (they may not be run on all servers but they are deployed to the whole list)

one misgiving about using live servers is that we don't always have all servers
running - for large numbers of servers deployments are going to be a problem
with this method

a solution would be to always deploy when we start a server

an alternative way would be to have the servers use git or some other tool to 
update themselves either periodically or after being externally prompted 
doing this would require setting up ssh keys or some other authentication
on the hosts once they are built
"""
try:
	import hosts
except:
	print("missing hosts module! run one of the hostmanager goals to create this")

from fabric.api import env, sudo, put, prompt, abort, local
from fabric.decorators import task, runs_once, parallel
import os

# currently this is locally hosted 
HELLO_REPO = os.environ['HELLO_REPO']

@runs_once
def _package_hello(path, tag):
	"""
	create a temporary git repo and check out a specific version
	having a bunch of deployment code along with the service is
	unusual - normally we'd want to only have exactly what we need
	"""
	repo_base = os.path.join('/tmp', 'hello_repos')
	repo = os.path.join(repo_base,tag)
	local('/bin/rm -fr {}'.format(repo_base))
	if not os.path.isdir(repo):
		local('mkdir -p {0}; cd {0} && git clone {1} {2}'.format(repo_base, HELLO_REPO, tag))

	# assuming a pretty simple branching structure here
	local('cd {} && git pull origin master && git checkout {}'.format(repo, tag))

	fullpath = os.path.join(repo, path)

	if os.path.isfile(fullpath):
		return fullpath

	abort("can't make package")
	
@task
@runs_once
def hello_deploy(tag=None):
	"""deploy version of the hello service to current hosts"""
	if tag is None:
		tag = prompt("Enter tag to retrieve: ",validate='^\w+$')
	_deploy_hello(tag)

@parallel
def _deploy_hello(tag):
	pkg = _package_hello('service/hello.py', tag)
	put(pkg, "/usr/share/nginx")

@task
@parallel
def hello_start():
	"""(re)starts the hello service on all servers"""
	# we could put this sort of thing into the kickstart file but servers may be repurposed
	sudo(
		"iptables -D INPUT -p tcp -m state --state NEW -m tcp --dport 9999 -j ACCEPT; "
		"iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 9999 -j ACCEPT; "
		"iptables -S; "
		"service iptables save"
	)
	# using bottle's own web server for now 
	# normally this would be run through nginx or apache using uwsgi or the like
	# similarly because the server only does something simple I'm not using virtualenv
	sudo(
		"cd /usr/share/nginx && "
		"( kill `cat hello.pid` 2>/dev/null || true; "
		"chmod a+x hello.py; "
		"echo starting hello.py now; "
		"nohup ./hello.py >hello.log 2>&1 & "
		"echo $! > hello.pid; "
		"sleep 5; "
		"cat hello.pid hello.log )"
	)
	sudo("netstat -ntlp")

@task
@parallel
def hello_stop():
	"""stops the hello service on all servers"""
	sudo("cd /usr/share/nginx && kill `cat hello.pid`")

@task
def hello_test():
	"""do basic sanity check of deployed hello service"""
	local("curl 'http://{}:9999/' | grep 'Hello World'".format(env.host))
	local("curl 'http://{}:9999/hello_test' | grep 'Method not allowed'".format(env.host))
	local("curl -XPOST 'http://{}:9999/hello_test' | grep 'Hello hello_test World'".format(env.host))

