#MySQL存储模块
import pymysql
from config import *


class MySQL():
    #初始化mysql
    def __init__(self, host=MYSQL_HOST, username=MYSQL_USER, password=MYSQL_PASSWORD, port=MYSQL_PORT, database=MYSQL_DATABASE):
        try:
            self.db = pymysql.connect(host, username, password, database, charset='utf8', port=port)
            self.cursor = self.db.cursor()
        except pymysql.MySQLError as e:
            print(e.args)

    #插入数据
    def insert(self, table, data):
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql_query = 'insert into %s (%s) values (%s)' % (table, keys, values)
        try:
            self.cursor.execute(sql_query, tuple(data.values()))
            self.db.commit()
        except pymysql.MySQLError as e:
            print(e.args)
            self.db.rollback()