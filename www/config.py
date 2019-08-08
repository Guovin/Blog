#！/user/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'Scuh'

'''
Configuration
'''

import config_default

class Dict(dict):
	'''
	Simple dict but support access as x.y style.
	定义一个继承dict的类，实现多种方式获取值，d.value=xxx或d['bb']=xxx
	'''

	def __init__(self,names=(),values=(),**kw):
		super(Dict,self).__init__(**kw)
		for k,v in zip(names,values):
			self[k] = v

	def __getattr__(self,key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

	def __setattr__(self,key,value):
		self[key] = value

#合并函数
def merge(defaults,override):
	r = {}
	for k,v in defaults.items():
		if k in override:
			if isinstance(v,dict): #当v为dict时递归，使其最终变为items（键、值分开的列元组）
				r[k] = merge(v,override[k])
			else:
				r[k] = override[k]
		else:
			r[k] = v
	return r

#将一个dict转为Dict
def toDict(d):
	D = Dict()
	for k,v in d.items():
		#使用三目运算符，如果是dict则递归，否则就直接赋值：
		D[k] = toDict(v) if isinstance(v,dict) else v
	return D

configs = config_default.configs

#合并设置：
try:
	import config_override
	configs = merge(configs,config_override.configs)
except ImportError:
	pass

configs = toDict(configs)