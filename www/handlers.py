#！/user/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'Scuh'

'''
'url handlers'
'''

import re,time,json,logging,hashlib,base64,asyncio

from coroweb import get,post

from models import User,Comment,Blog,next_id

@get('/')
async def index(request):
	users = await User.findAll()
	return{'__template__':'test.html','users':users}
	#注意users！！前者表示test.html要引用的，后一个是表示来自schema.sql定义的表。