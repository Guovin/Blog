#！/user/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'Scuh'

'''
Models for user,blog,comment.
'''

import time,uuid

from orm import Model,StringField,BooleanField,FloatField,TextField

def next_id():
	return '%015d%s000' % (int(time.time() * 1000),uuid.uuid4().hex)

#将所需的三个表用Model表示出来：
class User(Model):
	__table__ = 'users'

	id = StringField(primary_key=True,default=next_id,ddl='varchar(50)')
	email = StringField(ddl='varchar(50)')
	passwd = StringField(ddl='varchar(50)')
	admin = BooleanField()
	name = StringField(ddl='varchar(50)')
	image = StringField(ddl='varchar(500)')
	created_at = FloatField(name=None,column_type=float,primary_key=False,default=time.time)
    #time.time自动设置当前日期与时间。
    #日期和时间用float类型存储在数据库中，而不是datetime类型，这么做的好处是不必关心数据库的时区以及时区转换问题，
    #排序非常简单，显示的时候，只需要做一个float到str的转换，也非常容易。

class Blog(Model):
	__table__  = 'blogs'

	id = StringField(primary_key=True,default=next_id,ddl='varchar(50)')
	user_id = StringField(ddl='varchar(50)')
	user_name = StringField(ddl='varchar(50)')
	user_image = StringField(ddl='varchar(500)')
	name = StringField(ddl='varchar(50)')
	summary = StringField(ddl='varchar(200)')
	content = TextField()
	created_at = FloatField(name=None,column_type=float,primary_key=False,default=time.time)

class Comment(Model):
	__table__ = 'comments'

	id = StringField(primary_key=True,default=next_id,ddl='varchar(50)')
	blog_id = StringField(ddl='varchar(50)')
	user_id = StringField(ddl='varchar(50)')
	user_name = StringField(ddl='varchar(50)')
	user_image =StringField(ddl='varchar(500)')
	content = TextField()
	created_at = FloatField(name=None,column_type=float,primary_key=False,default=time.time)