import pymysql
from datetime import datetime

__all__ = ["DatabaseOperations"]


class DatabaseOperations:
    def __init__(self):
        # 数据库连接配置（保持不变）
        self.config = {
            "host": "43.240.13.41",
            "port": 3306,
            "user": "syxxdata",
            "password": "syxx123456",
            "database": "syxx_data",
            "charset": "utf8mb4",
            "auth_plugin_map": {'caching_sha2_password': 'mysql_native_password'}
        }
        self.conn = None
        self.cursor = None

    def connect(self):
        """连接数据库"""
        try:
            self.conn = pymysql.connect(**self.config)
            self.cursor = self.conn.cursor()
            print("数据库连接成功")
            return True
        except pymysql.MySQLError as e:
            print(f"数据库连接失败：{e}")
            self.conn = None
            self.cursor = None
            return False

    def close(self):
        """断开数据库连接"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            print("数据库连接已关闭")
        except pymysql.MySQLError as e:
            print(f"关闭数据库连接失败：{e}")

    def insert_data(self,SQL,Value):
        """插入数据"""
        if not self.conn or not self.cursor:
            print("数据库未连接，请先调用connect()方法")
            return False
            # 检查数据库连接状态
        try:
            # 执行插入
            self.cursor.execute(SQL,Value)
            self.conn.commit()
            print("数据插入成功！")
            return True

        except pymysql.MySQLError as e:
            print(datetime.now())
            print(f"插入数据失败：{e}")
            if self.conn:
                self.conn.rollback()
            return False
        except Exception as e:
            print(datetime.now())
            print(f"发生意外错误：{e}")
            return False

    def search_data(self,SQL):
        """查询所有数据"""
        if not self.conn or not self.cursor:
            print("数据库未连接，请先调用connect()方法")
            return False
        try:
            # 执行查询
            self.cursor.execute(SQL)
            # 获取所有结果
            results = self.cursor.fetchall()
            return results

        except pymysql.MySQLError as e:
            print(f"查询URL失败: {e}")
            return set()  # 异常时也返回空集合

    def drop_duplicate_data(self,SQL):
        """删除表中的重复URL记录"""
        if not self.conn or not self.cursor:
            print("数据库未连接，请先调用connect()方法")
            return False
        try:
            self.cursor.execute(SQL)
            self.conn.commit()
            print(f"删除了 {self.cursor.rowcount} 条重复记录")
        except pymysql.MySQLError as e:
            print(f"删除重复数据失败: {e}")
            self.conn.rollback()


