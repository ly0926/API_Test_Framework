import unittest

from library.HTMLTestRunnerNew import HTMLTestRunner

from common.handle_path import HandlePath
from common.handle_config import read_conf
from common.send_email import send_msg

# 第一步：创建测试套件
suite = unittest.TestSuite()

# 第二步加载用例到套件
loader = unittest.TestLoader()

suite.addTest(loader.discover(HandlePath.case_path))


# 第三步：创建一个测试用例运行程序
with open(HandlePath.report_path, "wb") as f:
    runner = HTMLTestRunner(stream=f,
                            title=read_conf.read_config('Project', 'PRO_NAME'),
                            description="测试报告的描述信息...",
                            tester=read_conf.read_config('Project', 'Tester'),
                            verbosity=2
                            )
    # 第一步：运行测试套件
    runner.run(suite)


# 执行完代码之后，发送报告
send_msg(HandlePath.report_path, "测试报告")

