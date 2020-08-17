import unittest
import decimal
import jsonpath
from common.handle_excel import ReadExcel
from common.handle_path import HandlePath
from library.ddt import ddt, data
from common.handle_config import read_conf
from common.handle_request import HandleSessionRequest
from common.handle_log import mylog
from common.handle_db import HandleDB
from common.handle_sign import HandleSign

from common.handle_data import TestData, replace_data, not_existed_member_id


@ddt
class TestRecharge(unittest.TestCase):
    excel = ReadExcel(HandlePath.data_path, "recharge")
    cases = excel.read_data()

    def setUp(self):
        self.http = HandleSessionRequest()
        # 创建操作数据库的对象
        self.db = HandleDB()
        # 登录，获取用户的id以及鉴权需要用到的token
        url = read_conf.get("env", "url") + "/member/login"
        data = {
            "mobile_phone": read_conf.getint("test_user_data", 'login_and_invest_tel'),
            "pwd": eval(read_conf.read_config("test_user_data", "login_and_invest_pwd"))
        }
        headers = eval(read_conf.get("env", "headers"))
        response = self.http.http_request(method="post", url=url, json=data, headers=headers)
        json_data = response.json()
        # -------登录之后，从响应结果中提取用户id和token-------------
        # 1、提取用户id
        member_id = jsonpath.jsonpath(json_data, "$..id")[0]
        setattr(TestData, "member_id", str(member_id))
        # 2、提取token
        token_type = jsonpath.jsonpath(json_data, "$..token_type")[0]
        token = jsonpath.jsonpath(json_data, "$..token")[0]
        setattr(TestData, "token", token)
        token_data = token_type + " " + token
        setattr(TestData, "token_data", token_data)

        setattr(TestData, "not_existed_member_id", str(not_existed_member_id()))

    def tearDown(self) -> None:
        self.http.close()
        self.db.close()

    @data(*cases)
    def test_recharge(self, case):
        # ------第一步：准备用例数据------------
        # 拼接完整的接口地址
        url =read_conf.get("env", "url") + case["URL"]
        # 请求的方法
        method = case["Method"]
        # 请求参数
        # 替换用例参数
        case["Data"] = replace_data(case["Data"])
        data = eval(case["Data"])
        # 获取sign和时间戳
        sign_data = HandleSign.generate_sign(getattr(TestData, "token"))
        # 将sign加入到请求参数中
        data.update(sign_data)
        # 请求头
        headers = eval(read_conf.get("env", "headers"))
        headers["Authorization"] = getattr(TestData, "token_data")

        # 预期结果
        expected = case["Expected"]
        # 该用例在表单的中所在行
        row = case["CaseId"] + 1

        TestResult = 'PASS'
        # SELECT leave_amount FROM futureloan.member WHERE mobile_phone = "{}"
        # ------第二步：发送请求到接口，获取实际结果--------
        if case["CheckSql"]:

            sql = case["CheckSql"]
            # 获取取充值之前的余额
            start_money = self.db.query(sql, args=[eval(read_conf.read_config("test_user_data", "login_and_invest_tel"))])["leave_amount"]
            # start_money = self.db.query(sql)["leave_amount"]
        mylog.info('开始执行充值-"{}"测试用例'.format(case["Title"]))
        response = self.http.http_request(url=url, method=method, json=data, headers=headers)
        result = response.json()
        self.excel.write_data(row=row, column=8, value=str(result))
        # -------第三步：比对预期结果和实际结果-----
        try:
            self.assertEqual(expected, result["code"])
            # self.assertEqual((expected["msg"]), result["msg"])
            if case["CheckSql"]:
                sql = case["CheckSql"]
                # 获取取充值之前的余额
                end_money = self.db.query(sql ,args=[eval(read_conf.read_config("test_user_data", "login_and_invest_tel"))])["leave_amount"]
                recharge_money = decimal.Decimal(str(data["amount"]))
                mylog.info("充值之前金额为{}\n，充值金额为：{}\n，充值之后金额为{}，".format(start_money, recharge_money, end_money))
                # 进行断言
                self.assertEqual(recharge_money, end_money - start_money)
            mylog.info("用例：{}--->执行通过".format(case["Title"]))
        except AssertionError as e:
            TestResult = 'Failed'
            mylog.info("用例：{}--->执行未通过".format(case["Title"]))
            print("预取结果：{}".format(expected))
            print("实际结果：{}".format(result))
            raise e
        finally:
            self.excel.write_data(row=row, column=9, value=TestResult)

