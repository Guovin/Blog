create user 'Blog'@'localhost' identified by '1234567';#创建连接用户，Blog为user，1234567为密码；
drop database if exists awesome;#若存在，删除数据库

-- drop user 'Blog'@'localhost';#user存在而创建失败时，单独执行此语句；

create database awesome;#创建数据库

use awesome;#切换使用数据库

#给予用户权限
grant select, insert, update, delete on awesome.* to 'Blog'@'localhost' identified by '1234567';

#创建表：
create table users(
	`id` varchar(50) not null, #注意用的是 `，如果用引号‘则报错！
	`email` varchar(50) not null,
	`passwd` varchar(50) not null,
	`admin` bool not null,
	`name` varchar(50) not null,
	`image` varchar(500) not null,
	`created_at` real not null,
	unique key `idx_email` (`email`),
	key `idx_create_at` (`created_at`),
	primary key (`id`)
)engine=innodb default charset=utf8;

create table blogs (
    `id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `name` varchar(50) not null,
    `summary` varchar(200) not null,
    `content` mediumtext not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table comments (
    `id` varchar(50) not null,
    `blog_id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `content` mediumtext not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;
