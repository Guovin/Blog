#！/user/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'Scuh'

import asyncio,logging,aiomysql

def log(sql,asgs=()):
	logging.info('SQL: %s' % sql)

#创建连接池
async def create_pool(loop,**kw):
	logging.info('create database connectionpool...')
	global __pool #全局变量储存连接池
	__pool = await aiomysql.create_pool(
		host=kw.get('host','localhost'),
		port=kw.get('port',3306),
		user=kw['user'],
		password=kw['password'],
		db=kw['db'],
		charset=kw.get('charset','utf8'), #缺省情况设置编码,注意是utf8，utf-8会报错！
		autocommit=kw.get('autocommit',True), #自动提交事务
		maxsize=kw.get('maxsize',10),
		minsize=kw.get('minsize',1),
		loop=loop
		)

#SELECT语句
async def select(sql,args,size=None):
	log(sql,args)
	global __pool
	async with __pool.get() as conn:
		async with conn.cursor(aiomysql.DictCursor) as cur:
			await cur.execute(sql.replace('?','%s'),args or ())
			#SQL占位符为?，Mysql占位符为%s,自动替换
			if size:
				rs = await cur.fetchmany(size) #获取指定数量记录
			else:
				rs = await cur.fetchall() #获取全部记录
		logging.info('rows returned: %s' % len(rs))
		return rs

#构建一个execute函数处理执行INSERT、UPDATE、DELETE所需参数
async def execute(sql,args,autocommit=True):
	log(sql)
	async with __pool.get() as conn:
		if not autocommit:
			await conn.begin()
		try:
			async with conn.cursor(aiomysql.DictCursor) as cur:
				await cur.execute(sql.replace('?','%s'),args)
				affected = cur.rowcount
			if not autocommit:
				await conn.commit()
		except BaseException as e:
			if not autocommit:
				await conn.rollback()
			raise
		return affected
#execute()函数和select()函数所不同的是，cursor对象不返回结果集，而是通过rowcount返回结果数。


def create_args_string(num):
	L = []
	for n in range(num):
		L.append('?')
	return ', '.join(L)

#各种Field类与其子类：
class Field(object):
	
	def __init__(self,name,column_type,primary_key,default):
		self.name = name
		self.column_type = column_type
		self.primary_key = primary_key
		self.default = default

	def __str__(self):
		return '<%s, %s:%s>' %(self.__class__.__name__,
			self.column_type,self.name)
#映射varchar:
class StringField(Field):
	
	def __init__(self,name=None,primary_key=False,default=None,
		ddl='varchar(100)'):
		super().__init__(name,ddl,primary_key,default)

class BooleanField(Field):
	
	def __init__(self,name=None,default=False):
		super().__init__(name,'boolean',False,default)

class IntegerField(Field):
	
	def __init__(self,name=None,Primary_key=False,default=0):
		super().__init__(name,'bigint',primary_key,default)

class FloatField(Field):
	
	def __init(self,name=None,primary_key=False,default=0.0):
		super().__init__(name,'real',primary_key,default)

class TextField(Field):
	
	def __init__(self,name=None,default=None):
		super().__init__(name,'text',False,default)

#通过metaclass:ModelMetaclass将具体的子类如User的映射信息读取出来
class ModelMetaclass(type):
	
	def __new__(cls,name,bases,attrs):
		#排除Model类本身：
		if name == 'Model':
			return type.__new__(cls,name,bases,attrs)
		#获取table的名称：
		tableName = attrs.get('__table__',None) or name
		logging.info('found model: %s (table: %s)' % (name,tableName))
		#获取所有的Field和主键名：
		mappings = dict()
		fields = []
		primaryKey = None
		for k,v in attrs.items():
			if isinstance(v,Field):
				logging.info('  found mapping: %s ==> %s' % (k,v))
				mappings[k] = v
				if v.primary_key:
					#找到主键：
					if primaryKey:
						raise Exception('Duplicate primary key for field: %s' % k)
					primaryKey = k
				else:
					fields.append(k)
		if not primaryKey:
			raise Exception('Primary key not found.')
		for k in mappings.keys():
			attrs.pop(k)
		escaped_fields = list(map(lambda f: '`%s`' % f,fields))
		attrs['__mappings__'] = mappings #保存属性和列的映射关系
		attrs['__tables__'] = tableName
		attrs['__primary_key__'] = primaryKey #主键属性名
		attrs['__fields__'] = fields #除主键外的属性名
		#构造默认的SELECT、INSERT、UPDATE、DELETE语句：
		attrs['__select__'] = 'select `%s`,%s from `%s`' % (primaryKey,', '.join(escaped_fields),tableName)
		attrs['__insert__'] = 'insert into `%s` (%s,`%s`) values (%s)' % (tableName,', '.join(escaped_fields),primaryKey,create_args_string(len(escaped_fields)+1))
		attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName,', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f),fields)),primaryKey)
		attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName,primaryKey)
		return type.__new__(cls,name,bases,attrs)
#任何继承自Model的类如User，会自动通过ModelMetaclass扫描映射关系，
#并储存到自身的类属性如__table__,__mappings__中。


#定义ORM映射的基类Model
class Model(dict,metaclass=ModelMetaclass):
#从dict继承，具备dict所有功能；
	def __init__(self,**kw):
		super(Model,self).__init__(**kw)

	def __getattr__(self,key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Model' object has no attribute '%s'" % key)

	def __setattr__(self,key,value):
		self[key] = value
	'''
	同时又实现了特殊方法__getattr__()和__setattr__()，
	因此又可以像引用普通字段那样写：
	>>> user['id']
	123
	>>> user.id
	123
	'''
	def getValue(self,key):
		return getattr(self,key,None)

	def getValueOrDefault(self,key):
		value = getattr(self,key,None)
		if value is None:
			field = self.__mappings__[key]
			if field.default is not None:
				value = field.default() if callable(field.default) else field.default
				logging.debug('using default value for %s: %s' % (key,str(value)))
				setattr(self,key,value)
		return value

#往Model类中添加class方法，让所有子类调用class方法：
	#根据WHERE条件查找：
	@classmethod
	async def findAll(cls,where=None,args=None,**kw): #async装饰，变成协程
		' find objects by where clause. '
		sql = [cls.__select__]
		if where:
			sql.append('where')
			sql.append(where)
		if args is None:
			args = []
		orderBy = kw.get('orderBy',None)
		if orderBy:
			sql.append('order by ')
			sql.append(orderBy)
		limit = kw.get('limit',None)
		if limit is not None:
			sql.append('limit')
			if isinstance(limit,int):
				sql.append('?')
				args.append(limit)
			elif isinstance(limit,tuple) and len(limit) == 2:
				sql.append('?, ?')
				args.extend(limit)
			else:
				raise ValueError('Invalid limit value: %s' % str(limit))
		rs = await select(' '.join(sql),args)
		return [cls(**r) for r in rs]
	#根据WHERE条件查找，返回的是整数，适用于select count(*)的类型：
	@classmethod
	async def findNumber(cls,selectField,where=None,args=None):
		' find number by select and where. '
		sql = ['select %s _num_ from `%s`' % (selectField,cls.__table__)]
		if where:
			sql.append('where')
			sql.append(where)
		rs = await select(' '.join(sql),args,1)
		if len(rs) == 0:
			return None
		return rs[0]['_num_']
#往Model类添加实例方法，可以让所有子类调用实例的方法：
	@classmethod
	async def find(cls,pk):
		' find object by primary key. '
		rs = await select('%s where `%s`=?' % (cls.__select__,cls.__primary_key__),[pk],1)
		if len(rs) == 0:
			return None
		return cls(**rs[0])

	async def save(self):
		args = list(map(self.getValueOrDefault,self.__fields__))
		args.append(self.getValueOrDefault(self.__primary_key__))
		rows = await execute(self.__insert__,args)
		if rows != 1:
			logging.warn('failed to insert record: affected rows: %s' % rows)

	async def update(self):
		args = list(map(self.getValue,self.__fields__))
		args.append(self.getValue(self.__primary_key__))
		rows = await execute(self.__update__,args)
		if rows != 1:
			logging.warn('failed to update by primary key: affected rows: %s' % rows)

	async def remove(self):
		args = [self.getValue(self.__primary_key__)]
		rows = await execute(self.__delete__,args)
		if rows !=1:
			logging.warn(' failed to remove by primary key: affected rows: %s' % rows)