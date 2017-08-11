#!/usr/bin/env python
"""
simple hello service with bottle
"""
from bottle import route, post, default_app, run

@route('/')
def hello_world():
	return 'Hello World!'

@post('/<you>')
def hello_you(you):
	return 'Hello {0} World!'.format(you)

if __name__ == '__main__':
	run(host='0.0.0.0',port='9999')
else:
	default_app()

