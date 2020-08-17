import requests


class HandleRequest:

    def http_request(self, method, url, **kwargs):
        return requests.request(method, url, **kwargs)


class HandleSessionRequest:
    """使用session鉴权的接口，使用这个类类发送请求"""

    def __init__(self):
        self.session = requests.session()

    def http_request(self, method, url, **kwargs):
        return self.session.request(method, url, **kwargs)

    def close(self):
        return self.session.close()


if __name__ == '__main__':
    # from common.handle_config import read_conf
    # http = HandleSessionRequest()
    #
    # url = read_conf.get("env", "url") + "/member/recharge"
    # data = {
    #     "mobile_id": 2074006,
    #     "amount": 100
    # }
    # headers = eval(read_conf.get("env", "headers"))
    # response = http.http_request(method="post", url=url, json=data, headers=headers)
    # json_data = response.json()
    # print(json_data)



    url = "http://api.lemonban.com/futureloan/loan/audit"

    # login_url = "http://api.lemonban.com/futureloan/member/login"

    data = {
        "loan_id": "",
        "approved_or_not": True,
        'timestamp': 1597217973,
        'sign': 'nwBNdbn8g+nYs7+PNXrRpdpLfY5yIgBabZpN3cHlf8DHdQ06VbgvePrd8OI22dtNhcjS4rpVxPj4UVkLBXoDHnoe9Un0E1ODmMPvy/CxaHR9rsDIlqp9oRk0MSG+sTh6dCfgPOGohJYjGg9CrPNQJ5yGtcENRVF/r+E3y4S4dHY='
    }
    header = {'X-Lemonban-Media-Type': 'lemonban.v3', 'Content-Type': 'application/json',
     'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJtZW1iZXJfaWQiOjIwNzQxMjgsImV4cCI6MTU5NzIxODQyNH0.CeVIwm17RBl5FJdN_EqobJiAu7lOlq2jnyFLHUrzGjME5wgcuI1Ji-HwoGFFzgOzh5y6ZO2O5fESDSFXzViohQ'}


    http = HandleSessionRequest()
    res1 = http.http_request(url=url, method="post", json=data, headers=header)
    # res2 = http.http_request(url=login_url, method="post", json=register_data, headers=header)

    print(res1.json())
    # print(res2.json())
