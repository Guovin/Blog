import orm,asyncio
from models import User,Blog,Comment

async def test(loop):
	#db要对应orm中__pool中的db：
	await orm.create_pool(loop=loop,user='Blog', password='1234567', db='awesome')
	u = User(name='asd', email='asd@example.com', passwd='1234567', image='about:blank')
	await u.save() 
	#保存数据到数据库。由于save方法在orm是由异步实现的，需要使用await的方法才能真正实现效果。

#调用循环执行：
loop=asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()#关闭


