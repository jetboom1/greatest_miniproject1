
from pprint import pprint


def read_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        file_as_string = file.read()
        return file_as_string


def parse_(file_):
    file = file_.split(') ')
    head = file.pop(0).split('\n\n')
    # парсинг окремих даних по ключах
    # тобто це словник де місто це ключ а вся інформація це значення
    lines = []
    # додавання шапки
    lines.append(head[:-1])
    # по кажному населеномц пункті
    for line in file:
        settlement = dict()
        # тепер проходимось кожному абзаці
        for part_of_line in line.split('\n\n'):
            if len(part_of_line) > 2:
                # якщо строчка містить назву міста
                if line.split('\n\n')[0] == part_of_line:
                    key = part_of_line.split(', ')[0]
                    value = part_of_line.split(', ')[1:]
                    time_dict_1 = {}
                    # на випадок якщо більше ніж одна церква в селі
                    for church in ', '.join(value).replace('\n', ' ').split('; '):
                        church = church.split(', ')
                        time_dict_1[church[0]] = church[1:]
                    settlement[key] = [time_dict_1]
                # якщо стрічка не мітить церкви
                else:
                    line_ = part_of_line.split(": ")
                    time_dict = {}
                    key_ = line_[0]
                    # якщо ключ строчки є школа
                    if key_ == 'Шк.':
                        value_ = line_[1].replace('\n', ' ').split(';')
                        time_list = []
                        for school in value_:
                            school = school.split(', ')
                            time_list.append(school)
                        time_dict[key_] = time_list
                        settlement[key].append(time_dict)
                    #  всі решту стрічки
                    else:
                        value = line_[1].replace('\n', ' ')
                        time_dict[key_] = value
                        settlement[key].append(time_dict)
        # додаємо населений пункт в список
        lines.append(settlement)
    return lines