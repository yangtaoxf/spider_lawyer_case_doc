import pymysql
from DBUtils.PooledDB import PooledDB, SharedDBConnection


# class Config(object):
#     POOL = PooledDB(creator=pymysql,  # 使用链接数据库的模块
#                     maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
#                     mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
#                     maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
#                     maxshared=3,
#                     # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
#                     blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
#                     maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
#                     setsession=[],
#                     ping=0,
#                     host='rm-wz9702rx253g2yhoivo.mysql.rds.aliyuncs.com',
#                     port=3306,
#                     user='duowenapp_b',
#                     password='duowenapp_b@11',
#                     db='duowen',
#                     charset='utf8',
#                     )


# class Config(object):
#     POOL = PooledDB(creator=pymysql,  # 使用链接数据库的模块
#                     maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
#                     mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
#                     maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
#                     maxshared=3,
#                     # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
#                     blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
#                     maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
#                     setsession=[],
#                     ping=0,
#                     host='120.76.138.153',
#                     port=3307,
#                     user='root',
#                     password='faduceshi123!@#',
#                     db='duowen',
#                     charset='utf8',
#                     )

class LawCaseConfig(object):
    POOL = PooledDB(creator=pymysql,  # 使用链接数据库的模块
                    maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
                    mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
                    maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
                    maxshared=3,
                    # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
                    blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
                    maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
                    setsession=[],
                    ping=0,
                    host='rm-wz9w950h9246dk9c7uo.mysql.rds.aliyuncs.com',
                    port=3306,
                    user='duowenapp_b',
                    password='duowenapp_b！666hh'.encode("utf8"),
                    use_unicode=True,
                    db='lawcase',
                    charset='utf8',
                    )
