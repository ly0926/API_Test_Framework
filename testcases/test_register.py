import unittest


from common.handle_excel import ReadExcel
from common.handle_path import HandlePath
from library.ddt import ddt, data
from common.handle_config import read_conf
from common.handle_request import HandleSessionRequest
from common.handle_log import mylog
from common.handle_db import HandleDB
from common.handle_data import TestData, no_reg_tel, exist_tel, replace_data


@ddt
class TestRegister(unittest.TestCase):
    excel = ReadExcel(HandlePath.data_path, "register")
    cases = excel.read_data()

    def setUp(self) -> None:
        self.http = HandleSessionRequest()
        self.db = HandleDB()

        setattr(TestData, "NoRegTel", no_reg_tel())
        setattr(TestData, "ExistTel", exist_tel())

    def tearDown(self):
        self.http.close()
        self.db.close()

    @data(*cases)
    def test_register(self, case):
        # ------第一步：准备用例数据------------
        # 拼接完整的接口地址
        url = read_conf.get("env", "url") + case["URL"]
        # 请求方法
        method = case["Method"]
        # 请求参数
        case["Data"] = replace_data(case["Data"])
        data = eval(case["Data"])

        # 判断是否有有手机号码需要替换
        # if "${ExistTel}" in case["Data"]:
        #     # 生成一个已存在的手机号码
        #     tel_num = handle_data.exist_tel()
        #     # 进行替换
        #     case["Data"] = case["Data"].replace("${ExistTel}", tel_num)
        #
        # elif "${NoRegTel}" in case["Data"]:
        #     # 生成一个未注册的手机号码
        #     tel_num = handle_data.no_reg_tel()
        #     # 进行替换
        #     case["Data"] = case["Data"].replace("${NoRegTel}", tel_num)

        # 请求头
        headers = eval(read_conf.get("env", "headers"))
        # 预期结果
        expected = case["Expected"]
        # 该用例在表单的中所在行
        row = case["CaseId"] + 1

        TestResult = 'PASS'

        # ------第二步：发送请求到接口，获取实际结果--------
        mylog.info('开始执行注册-"{}"测试用例'.format(case["Title"]))
        response = self.http.http_request(method=method, url=url, json=data, headers=headers)
        result = response.json()
        self.excel.write_data(row=row, column=8, value=str(result))

        # -------第三步：比对预期结果和实际结果-----
        try:
            self.assertEqual(expected, result["code"])
            if result["msg"] == "OK":
                # 去数据库查询当前注册的账号是否存在
                count = self.db.count("select * from member where mobile_phone=%s;", args=data["mobile_phone"])
                # 数据库中返回的数据做断言，判断是否有一条数据
                self.assertEqual(1, count)

            mylog.info("用例：{}--->执行通过".format(case["Title"]))

        except AssertionError as e:
            TestResult = 'Failed'
            mylog.info("用例：{}--->执行未通过".format(case["Title"]))
            mylog.error(e)
            print("预取结果：{}".format(expected))
            print(data["mobile_phone"])
            print("实际结果：{}".format(result))
            raise e

        finally:
            self.excel.write_data(row=row, column=9, value=TestResult)




