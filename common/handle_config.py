from configparser import ConfigParser
import yaml

from common.handle_path import HandlePath


class ReadConfig(ConfigParser):

    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.read(filename, encoding='utf-8')

    def read_config(self, section, option):
        return self.get(section, option)

    def write_config(self, section, options, value):
        if not self.has_section(section):
            self.add_section(section)
        self.set(section, options, value)
        with open(self.filename, encoding='utf-8', mode='w') as f:
            self.write(fp=f)


read_conf = ReadConfig(HandlePath.conf_path)


class ReadYaml:

    def __init__(self, filename):
        self.file_name = filename

    def read_yaml(self):
        with open(self.file_name, encoding='utf-8') as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)

    def write_yaml(self, data):
        with open(self.file_name, encoding='utf-8', mode='w') as f:
            yaml.dump(data=data, stream=f, allow_unicode=True)


read_yml = ReadYaml(HandlePath.yaml_path)


if __name__ == '__main__':
    # print(read_conf.get("env", "url")+"/member/register")
    # print(read_conf..get("env", "headers"))

    read_conf.write_config('hero', 'name', "蓝蓝")

    # print(read_yml.read_yaml())


