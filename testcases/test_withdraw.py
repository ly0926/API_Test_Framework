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
from common.handle_data import TestData, replace_data
from common.handle_sign import HandleSign


@ddt
class TestWithdraw(unittest.TestCase):
    excel = ReadExcel(HandlePath.data_path, "withdraw")
    cases = excel.read_data()

    def setUp(self) -> None:
        self.http = HandleSessionRequest()
        self.db = HandleDB()

    def tearDown(self):
        self.http.close()
        self.db.close()

    @data(*cases)
    def test_withdraw(self, case):
        # ------第一步：准备用例数据------------
        # 拼接完整的接口地址
        url = read_conf.read_config("env", "url") + case["URL"]
        # 请求的方法
        method = case["Method"]
        # 请求参数
        # 判断是否有用户id需要替换
        case["Data"] = replace_data(case["Data"])
        data = eval(case["Data"])

        # 请求头
        headers = eval(read_conf.read_config("env", "headers"))
        if case["Moudle"] !="login":
            headers["Authorization"] = getattr(TestData,"token_data")
            # 获取sign和时间戳
            sign_data = HandleSign.generate_sign(getattr(TestData, "token"))
            # 将sign加入到请求参数中
            data.update(sign_data)
        # 预期结果
        expected = case["Expected"]
        # 该用例在表单的中所在行
        row = case["CaseId"] + 1

        TestResult = 'PASS'
        # ------第二步：发送请求到接口，获取实际结果--------
        # 判断是否需要sql校验
        if case["CheckSql"]:
            sql = case["CheckSql"]
            # 获取取充值之前的余额
            start_money = self.db.query(sql, args=[data["member_id"]])["leave_amount"]

        mylog.info('开始执行提现-"{}"测试用例'.format(case["Title"]))
        # 发送请求，获取结果
        response = self.http.http_request(url=url, method=method, json=data, headers=headers)
        result = response.json()
        self.excel.write_data(row=row, column=8, value=str(result))

        if case["Moudle"] == "login":
            # -------如果是登录接口，从响应结果中提取用户id和token-------------
            # 1、用户id
            member_id = jsonpath.jsonpath(result, "$..id")[0]
            setattr(TestData, "member_id", str(member_id))
            # 2、提取token
            token_type = jsonpath.jsonpath(result, "$..token_type")[0]
            token = jsonpath.jsonpath(result, "$..token")[0]
            setattr(TestData, "token", token)
            token_data = token_type + " " + token
            setattr(TestData, "token_data", token_data)

        # -------第三步：比对预期结果和实际结果-----
        try:
            self.assertEqual(expected, result["code"])
            # self.assertEqual((expected["msg"]), result["msg"])
            # 判断是否需要数据库校验
            if case["CheckSql"]:
                sql = case["CheckSql"]
                # 获取取充值之前的余额
                end_money = self.db.query(sql, args=[data["member_id"]])["leave_amount"]
                recharge_money = decimal.Decimal(str(data["amount"]))
                mylog.info("取现之前金额为{}\n，取现金额为：{}\n，取现之后金额为{}，".format(start_money, recharge_money, end_money))
                # 进行断言(开始的金额减去结束的金额)
                self.assertEqual(recharge_money, start_money - end_money)
            mylog.info("用例：{}--->执行通过".format(case["Title"]))

        except AssertionError as e:
            TestResult = 'Failed'
            mylog.info("用例：{}--->执行未通过".format(case["Title"]))
            print("预取结果：{}".format(expected))
            print("实际结果：{}".format(result))
            raise e
        finally:
            self.excel.write_data(row=row, column=9, value=TestResult)
