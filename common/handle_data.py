import re
import random

from common.handle_config import read_conf
from common.handle_db import HandleDB


def exist_tel():
    """生成一个已注册的手机号"""
    return HandleDB().query(sql="SELECT mobile_phone FROM member LIMIT 1;")["mobile_phone"]


def generator_phone():
    """生成一个随机的手机号"""
    prelist = ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139", "147", "150", "151", "152",
               "153", "155", "156", "157", "158", "159", "176", "177","178", "180", "185", "186", "187","188", "189"]

    return random.choice(prelist) + "".join(random.choice("0123456789") for i in range(8))


def no_reg_tel():
    """生成一个未注册的手机号"""
    while True:
        tel_num = generator_phone()
        if not HandleDB().query("select * from member where mobile_phone=%s;", args=[tel_num]):
            break
    return tel_num


def not_existed_member_id():
    """生成一个不存在的id号"""
    return HandleDB().query(sql="SELECT max(id) FROM member LIMIT 1;")["max(id)"] + 1


class TestData:
    """这个类的作用：专门用来处理临时数据，以及解决用例关联问题"""
    # ExistTel = exist_tel()
    # NoRegTel = no_reg_tel()
    # not_existed_member_id = not_existed_member_id()
    # member_id = None
    # token = ""
    # token_data = ""


def replace_data(data):
    r = r"\$\{(.+?)\}"
    # 判断是否有需要替换的数据
    while re.search(r, data):
        # 匹配出第一个要替换的数据
        res = re.search(r, data)
        # 提取待替换的内容
        item = res.group()
        # 获取替换内容中的数据项
        key = res.group(1)
        try:
            # 根据替换内容中的数据项去配置文件中找到对应的内容，进行替换
            # data = data.replace(item, read_conf.get("test_user_data", key))
            data = data.replace(item, str(getattr(TestData, key)))
        except:
            data = data.replace(item, read_conf.get("test_user_data", key))
    # 返回替换好的数据
    return data


if __name__ == '__main__':
    # print(getattr(TestData, 'NoRegTel'))
    # s = '{"member_id": "${Invest_user_id}", "pwd": "12345678"}
    # res = re.search('\$\{(.+?)\}',s)
    # print(res)
    # print(res.group(0))
    # print(res.group(1))
    # print(getattr(TestData, "NoRegTel "))
    print(not_existed_member_id())