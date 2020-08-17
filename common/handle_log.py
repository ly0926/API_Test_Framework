import logging

from common.handle_config import read_conf
from common.handle_path import HandlePath


# 读取配置文件中的数据
log_name = read_conf.get("logging", "log_name")
log_level = read_conf.get("logging", "level")
f_level = read_conf.get("logging", "f_level")
s_level = read_conf.get("logging", "s_level")


class MyLogger(logging.Logger):

    def __init__(self,
                 name=log_name,
                 level=log_level,
                 file=None,
                 fmt="[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d][%(levelname)s][%(message)s]"):
        super().__init__(name)

        self.setLevel(level)

        format = logging.Formatter(fmt)

        # handler
        if file:
            file_handler = logging.FileHandler(file, encoding="utf8")
            file_handler.setLevel(level)
            file_handler.setFormatter(format)
            self.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(format)
        self.addHandler(stream_handler)


class MyLogger_1:

    @staticmethod
    def create_logger():
        # 一、创建日志收集器
        my_log = logging.getLogger(log_name)
        # 二、设置日志收集器的等级
        my_log.setLevel(log_level)
        # 三、添加输出渠道（输出到控制台）
        # 1、创建一个输出到控制台的输出渠道
        sh = logging.StreamHandler()
        # 2、设置输出等级
        sh.setLevel(s_level)
        # 3、将输出渠道绑定到日志收集器上
        my_log.addHandler(sh)
        # 四、添加输出渠道（输出到文件）
        fh = logging.FileHandler(HandlePath.log_path, encoding="utf8")
        fh.setLevel(f_level)
        my_log.addHandler(fh)
        # 五、设置日志输出的格式
        # 创建一个日志输出格式
        formatter = logging.Formatter('[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d][%(levelname)s][%(message)s]')
        # 将输出格式和输出渠道进行绑定
        sh.setFormatter(formatter)
        fh.setFormatter(formatter)

        return my_log


mylog = MyLogger(log_name, log_level, HandlePath.log_path)
mylog1 = MyLogger_1().create_logger()

if __name__ == '__main__':
    mylog.debug('这是一个debug信息')
    mylog.info("这是一个info信息")
    mylog.warning("这是一个warning信息")
    mylog.error("这是一条error信息")