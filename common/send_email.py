import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from common.handle_config import read_conf


now = time.strftime('%Y-%m-%d-%H-%M-%S')


def send_msg(filename, title):

    # 第一步： 实例化smtp服务器并登录
    smtp = smtplib.SMTP_SSL(host=read_conf.get("email", "host"), port=read_conf.getint("email", "port"))  # 端口
    smtp.login(user=read_conf.get("email", "user"), password=read_conf.get("email", "pwd"))  # 登录，帐号加授权码

    # 第二步：构建邮件
    msg = MIMEMultipart()

    # 邮件文本内容
    text_smg = MIMEText(open(filename, 'r', encoding='utf8').read(),  _subtype="html", _charset="utf8")
    msg.attach(text_smg)

    # 创建附件
    file = MIMEApplication(open(filename, "rb").read())
    file.add_header('content-disposition', 'attachment', filename="{}report.html".format(now))
    msg.attach(file)

    msg["Subject"] = title      # 邮件主题
    msg["From"] = read_conf.get("email", "from_addr")      # 发件人
    msg["To"] = read_conf.get("email", "to_addr")     # 收件人

    # 第三步发送邮件
    smtp.send_message(msg, from_addr=read_conf.get("email", "from_addr"), to_addrs=read_conf.get("email", "to_addr"))

    # 关闭stmp服务
    smtp.close()


