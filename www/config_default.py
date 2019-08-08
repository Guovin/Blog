#！/user/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'Scuh'

'''
Default configgurations.
'''

configs = {
	'debug':True,
	'db':{
	'host':'127.0.0.1',
	'port':3306,
	'user':'Such',
	'password':'1234567',
	'db':'awesome'
	},
	'session':{
	'secret':'Awesome'
	}
}

print(configs.items())