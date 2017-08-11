#!/usr/bin/env python
"""
manage starting and checking servers
in this case we keep a list of vms that we can use
and start new vms when responses are too slow
or shut down vms when we may have too many running

unlike the fabric goals this is meant to run in the background
"""
import envmanager

def sla_check():
	"""
    makes a request to the load balancer and returns the response time
    if the response is more/less than what is expected for that environment
    add or remove servers as needed
    """
	pass



