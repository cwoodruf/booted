"""
this module maps virtualbox images and services to environments
the "service" key refers to deploy goals all starting with that key
we assume that the servers are divided between two different roles:
servers that handle external requests (loadbalancers) and servers that do actual work
"""
groups = {
	'prod': {
		'images': ['fabric1','ifabric2','fabric'],
		'roles': {
			'loadbalancers': ['fabric'],
			'workers': ['fabric1','ifabric2'],
		},
		'version': 'HELLO3',
		'service': 'hello',
	},
	'test': {
		'images': ['ifabric3'],
		'roles': {
			'loadbalancers': ['ifabric3'],
			'workers': ['ifabric3'],
		},
		'version': 'HELLO4',
		'service': 'hello',
	},
	'dev': {
		'images': ['ifabric4'],
		'roles': {
			'loadbalancers': ['ifabric4'],
			'workers': ['ifabric4'],
		},
		'version': 'HELLO4',
		'service': 'hello',
	},
}

