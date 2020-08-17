import unittest
import jsonpath
from library.ddt import ddt, data
from common.handle_excel import ReadExcel
from common.handle_path import HandlePath
from common.handle_db import HandleDB
from common.handle_config import read_conf
from common.handle_request import HandleSessionRequest
from common.handle_data import TestData, replace_data
from common.handle_log import mylog
from common.handle_sign import HandleSign


@ddt
class TestAudit(unittest.TestCase):
    excel = ReadExcel(HandlePath.data_path, "audit")
    cases = excel.read_data()

    # def setUp(self) -> None:
    #     self.http = HandleSessionRequest()
    #     self.db = HandleDB()
    #
    # def tearDown(self):
    #     self.http.close()
    #     self.db.close()

    @classmethod
    def setUpClass(cls):
        # -----------执行用例之前先进行登录-->
        # 登录，获取用户的id以及鉴权需要用到的token
        url = read_conf.read_config("env", "url") + "/member/login"
        data = {
            "mobile_phone": read_conf.read_config("test_user_data", 'admin_tel'),
            "pwd": eval(read_conf.read_config("test_user_data", "admin_pwd"))
        }
        headers = eval(read_conf.read_config("env", "headers"))
        response = HandleSessionRequest().http_request(url=url, method="post", json=data, headers=headers)
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

    def setUp(self) -> None:
        self.http = HandleSessionRequest()
        self.db = HandleDB()
        # ---------每个审核的用例执行之前都加一个项目，将项目id保存起来----------
        url = read_conf.read_config("env", "url") + "/loan/add"
        data = {"member_id": getattr(TestData, "member_id"),
                "title": "借钱实现财富自由",
                "amount": 2000,
                "loan_rate": 12.0,
                "loan_term": 3,
                "loan_date_type": 1,
                "bidding_days": 5}
        # 获取sign和时间戳
        sign_data = HandleSign.generate_sign(getattr(TestData, "token"))
        # 将sign加入到请求参数中
        data.update(sign_data)
        headers = eval(read_conf.read_config("env", "headers"))
        headers["Authorization"] = getattr(TestData, "token_data")
        # 发送请求加标
        response = self.http.http_request(url=url, method="post", json=data, headers=headers)
        json_data = response.json()
        # 1、提取标id
        loan_id = jsonpath.jsonpath(json_data, "$..id")[0]
        # 2、保存为TestDate的属性
        setattr(TestData, "loan_id", loan_id)

        setattr(TestData, "not_existed_loan_id", loan_id + 100)
        setattr(TestData, "not_status_on_audit_loan_id", loan_id - 1)

    def tearDown(self):
        self.http.close()
        self.db.close()

    @data(*cases)
    def test_audit(self, case):
        # 拼接完整的接口地址
        url = read_conf.read_config("env", "url") + case["URL"]
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
        headers = eval(read_conf.read_config("env", "headers"))
        headers["Authorization"] = getattr(TestData, "token_data")

        # 预期结果
        expected = eval(case["Expected"])
        # 该用例在表单的中所在行
        row = case["CaseId"] + 1

        TestResult = 'PASS'

        # ------第二步：发送请求到接口，获取实际结果--------
        mylog.info('开始执行审核-"{}"测试用例'.format(case["Title"]))
        response = self.http.http_request(url=url, method=method, json=data, headers=headers)
        result = response.json()

        self.excel.write_data(row=row, column=8, value=str(result))
        # 如果审核通过的项目返回ok，说明该项目已审核
        if case["Title"] == "审核通过" and result["msg"] == "OK":
            pass_loan_id = getattr(TestData, "loan_id")
            # 将该项目的id保存起来
            setattr(TestData, "pass_loan_id", pass_loan_id)

        # -------第三步：比对预期结果和实际结果-----
        try:
            self.assertEqual((expected["code"]), result["code"])
            self.assertEqual((expected["msg"]), result["msg"])
            if case["CheckSql"]:
                sql = replace_data(case["CheckSql"])
                # 获取这个标的用户id
                status = self.db.query(sql)["status"]
                # 进行断言
                self.assertEqual(expected["status"], status)
            mylog.info("用例：{}--->执行通过".format(case["Title"]))
        except AssertionError as e:
            TestResult = 'Failed'
            self.excel.write_data(row=row, column=8, value="未通过")
            mylog.info("用例：{}--->执行未通过".format(case["Title"]))
            print("预取结果：{}".format(expected))
            print("实际结果：{}".format(result))
            raise e

        finally:
            self.excel.write_data(row=row, column=9, value=TestResult)
