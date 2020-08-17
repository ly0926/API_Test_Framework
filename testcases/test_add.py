import unittest
import jsonpath
from library.ddt import ddt, data
from common.handle_excel import ReadExcel
from common.handle_path import HandlePath
from common.handle_config import read_conf
from common.handle_data import replace_data, TestData, not_existed_member_id
from common.handle_request import HandleSessionRequest
from common.handle_log import mylog
from common.handle_db import HandleDB
from common.handle_sign import HandleSign



@ddt
class TestAdd(unittest.TestCase):
    excel = ReadExcel(HandlePath.data_path, "add")
    cases = excel.read_data()

    def setUp(self) -> None:
        self.http = HandleSessionRequest()
        self.db = HandleDB()

        setattr(TestData, "not_existed_member_id", str(not_existed_member_id()))

    def tearDown(self):
        self.http.close()
        self.db.close()

    @data(*cases)
    def test_add(self, case):
        # 第一步：准备用例数据
        # 获取url
        url = read_conf.read_config("env", "url") + case["URL"]
        # url = conf.get_str("env", "url") + case.url
        # 获取数据
        case["Data"] = replace_data(case["Data"])
        data = eval(case["Data"])
        # 请求头
        headers = eval(read_conf.get("env", "headers"))
        if case["Moudle"] != "login":
            headers["Authorization"] = getattr(TestData, "token_data")
            # 获取sign和时间戳
            sign_data = HandleSign.generate_sign(getattr(TestData, "token"))
            # 将sign加入到请求参数中
            data.update(sign_data)
        # 预期结果
        expected = case["Expected"]
        # 请求方法
        method = case["Method"]
        # 用例所在的行
        row = case["CaseId"] + 1

        TestResult = 'PASS'
        # 第二步：发送请求
        if case["CheckSql"]:
            sql = replace_data(case["CheckSql"])
            s_loan_num = self.db.count(sql)

        mylog.info('开始执行加标-"{}"测试用例'.format(case["Title"]))
        res = self.http.http_request(url=url, method=method, json=data, headers=headers)
        json_data = res.json()
        self.excel.write_data(row=row, column=8, value=str(json_data))

        if case["Moudle"] == "login":
            # 如果是登录的用例，提取对应的token,和用户id,保存为TestData这个类的类属性，用来给后面的用例替换
            token_type = jsonpath.jsonpath(json_data, "$..token_type")[0]
            token = jsonpath.jsonpath(json_data, "$..token")[0]
            token_data = token_type + " " + token
            setattr(TestData, "token_data", token_data)
            setattr(TestData, "token", token)
            loan_id = jsonpath.jsonpath(json_data, "$..id")[0]
            setattr(TestData, "loan_id", str(loan_id))
        # 第三步：断言
        try:
            self.assertEqual(expected, json_data["code"])
            # self.assertEqual(expected["msg"], json_data["msg"])
            # 判断是否需要sql校验
            if case["CheckSql"]:
                sql = replace_data(case["CheckSql"])
                end_loan_num = self.db.count(sql)
                self.assertEqual(end_loan_num - s_loan_num, 1)
            mylog.info("用例：{}--->执行通过".format(case["Title"]))
        except AssertionError as e:
            TestResult = 'Failed'
            # self.excel.write_data(row=row, column=8, value="未通过")
            mylog.info("用例：{}--->执行未通过".format(case["Title"]))
            print("预取结果：{}".format(expected))
            print("实际结果：{}".format(json_data))
            raise e

        finally:
            self.excel.write_data(row=row, column=9, value=TestResult)
