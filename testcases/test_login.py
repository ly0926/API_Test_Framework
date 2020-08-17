import unittest
import random
from library.ddt import ddt, data

from common.handle_excel import ReadExcel
from common.handle_path import HandlePath
from common.handle_config import read_conf
from common.handle_request import HandleSessionRequest
from common.handle_log import mylog
from common.handle_db import HandleDB
from common import handle_data


@ddt
class TestLogin(unittest.TestCase):
    excel = ReadExcel(HandlePath.data_path, "login")
    cases = excel.read_data()

    def setUp(self) -> None:
        self.http = HandleSessionRequest()
        self.db = HandleDB()

        setattr(handle_data.TestData, "NoRegTel", handle_data.no_reg_tel())

    def tearDown(self):
        self.http.close()
        self.db.close()

    @data(*cases)
    def test_login(self, case):
        # ------第一步：准备用例数据------------
        # 拼接完整的接口地址
        url = read_conf.get("env", "url") + case["URL"]
        # 请求的方法
        method = case["Method"]

        # if "${normal_tel}" in case["Data"]:
        #     # 读取配置文件中登录专用信息
        #     user_info = eval(read_conf.read_config("test_user_data", "login_and_invest_info"))
        #     # 进行替换手机号
        #     case["Data"] = case["Data"].replace("${normal_tel}", user_info["mobile_phone"])
        #
        # elif "${NoRegTel}" in case["Data"]:
        #     tel_num = handle_data.no_reg_tel()
        #     # 进行替换
        #     case["Data"] = case["Data"].replace("${NoRegTel}", tel_num)
        # 请求参数
        case["Data"] = handle_data.replace_data(case["Data"])
        data = eval(case["Data"])
        # 请求头
        headers = eval(read_conf.get("env", "headers"))
        # 预期结果
        expected = case["Expected"]
        # 该用例在表单的中所在行
        row = case["CaseId"]+1

        TestResult = 'PASS'
        # ------第二步：发送请求到接口，获取实际结果--------
        mylog.info('开始执行登录-"{}"测试用例'.format(case["Title"]))
        response = self.http.http_request(method=method, url=url, json=data, headers=headers)
        result = response.json()
        self.excel.write_data(row=row, column=8, value=str(result))

        # -------第三步：比对预期结果和实际结果-----

        try:
            # 业务码断言
            self.assertEqual(expected, result["code"])
            # msg断言
            # self.assertEqual((expected["msg"]), result["msg"])
            mylog.info("用例：{}--->执行通过".format(case["Title"]))
        except AssertionError as e:
            TestResult = 'Failed'
            # 记录apicases.xlsx日志
            mylog.info("用例：{}--->执行未通过".format(case["Title"]))
            mylog.error(e)
            # 报告中打印预期和实际结果
            print("预取结果：{}".format(expected))
            print(data["mobile_phone"])
            print("实际结果：{}".format(result))
            raise e
        finally:
            self.excel.write_data(row=row, column=9, value=TestResult)



