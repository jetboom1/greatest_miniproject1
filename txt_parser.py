
from pprint import pprint


def read_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        file_as_string = file.read()
        return file_as_string


def parse_(file_):
    file = file_.split(') ')
    # парсинг окремих даних по ключах
    lines = []
    for line in file:
        l = dict()
        for part_of_line in line.split('\n\n'):
            if len(part_of_line) > 2:
                if line.split('\n\n')[0] == part_of_line:
                    # list_
                    key = part_of_line.split(', ')[0]
                    value = part_of_line.split(', ')[1:]
                    time_dict_1 = {}
                    time_dict_1[value[0]] = value[1:]
                    l[key] = [time_dict_1]
                else:
                    line_ = part_of_line.split(": ")
                    time_dict = {}
                    key_ = line_[0]
                    value_ = line_[1].replace('\n', ' ')
                    time_dict[key_] = value_
                    l[key].append(time_dict)

        lines.append(l)
    return lines