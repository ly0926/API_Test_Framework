import unittest
import jsonpath
from library.ddt import ddt, data
from common.handle_excel import ReadExcel
from common.handle_path import HandlePath
from common.handle_config import read_conf
from common.handle_data import replace_data, TestData
from common.handle_request import HandleSessionRequest
from common.handle_log import mylog
from common.handle_sign import HandleSign
from common.handle_db import HandleDB


@ddt
class TestInvest(unittest.TestCase):
    excel = ReadExcel(HandlePath.data_path, "invest")
    cases = excel.read_data()

    def setUp(self) -> None:
        self.http = HandleSessionRequest()
        self.db = HandleDB()

    def tearDown(self):
        self.http.close()
        self.db.close()

    @data(*cases)
    def test_invest(self, case):
        # 第一步：准备用例数据
        url = read_conf.read_config("env", "url") + case["URL"]
        # 请求参数
        case["Data"] = replace_data(case["Data"])
        data = eval(case["Data"])
        # 请求的方法
        method = case["Method"]
        # 请求头
        headers = eval(read_conf.read_config("env", "headers"))
        if case["Moudle"] != "login":
            headers["Authorization"] = getattr(TestData, "token_data")
            # 获取sign和时间戳
            sign_data = HandleSign.generate_sign(getattr(TestData, "token"))
            # 将sign加入到请求参数中
            data.update(sign_data)
            # 添加请求头中的token
        # 预期结果
        expected = eval(case["Expected"])
        # 用例所在行
        row = case["CaseId"] + 1

        TestResult = 'PASS'

        # 第二步：发送请求
        mylog.info('开始执行投资-"{}"测试用例'.format(case["Title"]))
        res = self.http.http_request(url=url, json=data, method=method, headers=headers)
        result = res.json()
        self.excel.write_data(row=row, column=8, value=str(result))
        if case["Moudle"] == "login":
            # 提取用户id和token
            token_type = jsonpath.jsonpath(result, "$..token_type")[0]
            token = jsonpath.jsonpath(result, "$..token")[0]
            token_data = token_type + " " + token
            id = jsonpath.jsonpath(result, "$..id")[0]
            setattr(TestData, "token", token)
            setattr(TestData, "token_data", token_data)
            setattr(TestData, "member_id", str(id))

        elif case["Moudle"] == "add":
            # 提取项目id
            loan_id = jsonpath.jsonpath(result, "$..id")[0]
            setattr(TestData, "loan_id", str(loan_id))

        # 第三步：比对结果（断言）
        try:
            self.assertEqual(expected["code"], result["code"])
            # self.assertEqual(expected["msg"], result["msg"])
            # 判断是否需要sql校验

            mylog.info("用例：{}--->执行通过".format(case["Title"]))
        except AssertionError as e:
            TestResult = 'Failed'
            mylog.info("用例：{}--->执行未通过".format(case["Title"]))
            print("预取结果：{}".format(expected))
            print("实际结果：{}".format(result))
            raise e
        finally:
            self.excel.write_data(row=row, column=9, value=TestResult)
