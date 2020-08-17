import pymysql

from common.handle_config import read_conf


class HandleDB:

    def __init__(self):
        # 读取数据库配置
        db_config = eval(read_conf.get('mysql', 'db_config'))
        # 创建连接对象，连接到数据库
        self.con = pymysql.connect(**db_config)
        # 创建游标对象
        self.cur = self.con.cursor()

    def query(self, sql, args=None, one=True):
        self.cur.execute(sql, args)
        self.con.commit()
        if one:
            """获取查询到的第一条数据"""
            return self.cur.fetchone()
        else:
            """获取sql语句查询到的所有数据"""
            return self.cur.fetchall()

    def count(self, sql, args=None):
        """获取sql语句查询到的所有数据"""
        self.con.commit()
        return self.cur.execute(sql, args)

    def close(self):
        # 关闭游标对象
        self.cur.close()
        # 断开连接
        self.con.close()


if __name__ == '__main__':
    sql = "SELECT leave_amount FROM member WHERE id=${member_id"
    # sql ="select * from member limit 3"
    # 获取取充值之前的余额
    start_money = HandleDB().query(sql)
    print(start_money)