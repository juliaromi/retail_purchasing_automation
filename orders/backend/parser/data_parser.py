import yaml
from pprint import pprint

def read_file(file):
    with open(file, encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        pprint(data)
        return data


if __name__ == '__main__':
    read_file('shop1.yaml')
