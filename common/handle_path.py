import os
import time

"""
该模块用来做路径处理
"""

t_s = str(time.strftime('%Y%m%d-%H%M%S'))
report_name = "{}report.html".format(t_s)
log_name = "test_log_{}.log".format(t_s)

def create_dir(path):
    """创建HTML报告与日志文件存放目录"""
    if not os.path.exists(path):
        os.makedirs(path)
    return path

class HandlePath:

    # 项目路径
    project_path = os.path.dirname(os.path.dirname(__file__))

    # 配置文件的路径
    conf_path = os.path.join(project_path, "conf", "conf.ini")
    yaml_path = os.path.join(project_path, "conf", "conf.yaml")

    # 用例数据的目录
    data_path = os.path.join(project_path, "data", "testData.xlsx")

    # 日志文件目录
    log_path = os.path.join(create_dir(os.path.join(project_path, "log")), log_name)

    # 测试报告路径
    report_path = os.path.join(create_dir(os.path.join(project_path, "report")), report_name)

    # 测试用例路径
    case_path = os.path.join(project_path, "testcases")


if __name__ == '__main__':
    print(HandlePath.log_path)