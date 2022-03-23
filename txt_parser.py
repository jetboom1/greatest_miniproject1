from pprint import pprint
from geopy import Nominatim
from geopy.exc import GeocoderUnavailable
from geopy.extra.rate_limiter import RateLimiter
from church_parser import church_parser
import re
import json


def read_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        file_as_string = file.read()
        return file_as_string


def header(protosfiterat, dekanat, settlement):
    geolocator = Nominatim(user_agent="University")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    try:
        founded_result = geolocator.geocode(settlement)
        result = {
            "протопресвітерат": protosfiterat,
            "деканат": dekanat,
            "населений пункт": {
                "назва": settlement,
                "location": {
                    "lat": founded_result.latitude,
                    "lng": founded_result.longitude
                }
            }
        }
    except (AttributeError, GeocoderUnavailable):
        result = {
            "протопресвітерат": protosfiterat,
            "деканат": dekanat,
            "населений пункт": {
                "назва": settlement,
                "location": {
                    "lat": 'not found',
                    "lng": 'not found'
                }
            }
        }
    return result


def parse_(file_):
    file = file_.split(') ')
    head = file.pop(0).split('\n\n')
    # тобто це словник де місто це ключ а вся інформація це значення
    lines = []
    # додавання шапки
    lines.append(head[:-1])
    # по кажному населеному пункті
    for line in file:
        settlement = dict()
        # тепер проходимось кожному абзаці
        for part_of_line in line.split('\n\n'):
            if len(part_of_line) > 2:
                # якщо строчка містить назву міста
                if line.split('\n\n')[0] == part_of_line:
                    key = part_of_line.split(', ')[0]
                    value = part_of_line.split(', ')[1:]
                    churches = church_parser(', '.join(value).replace('\n', ' ').split('; '))
                    settlement[key] = [header(head[1].split()[0], head[0].split()[0], key)]
                    settlement[key].append(churches)
                # якщо стрічка не мітить церкви
                else:
                    line_ = part_of_line.split(":")
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
                    elif key_ == 'Надає':
                        time_dict[key_] = line_[1].replace('\n', ' ')
                        settlement[key].append(time_dict)
                    elif key_ == 'Душ':
                        values = line_[1].replace('\n', ' ').split(';')
                        other = ''
                        time_dict[key_] = []
                        general_dict = {}
                        other_dict = None
                        pril_dict = None
                        if len(values) > 1:
                            other = values[-1]
                            other_dict = {'інше': other}
                            values.pop(-1)
                        for elements in values:
                            if not elements.strip().startswith('в прил.'):
                                for element in elements.split(', '):
                                    try:
                                        general_dict[element.split('.')[0]] = element.split('.')[1].strip()
                                    except IndexError:
                                        continue
                            else:
                                pril_info = elements.strip()[8:]
                                end_of_name = re.search('\s[а-яі]{3}[.]{1}', pril_info).span()[0]
                                pril_name = pril_info[:end_of_name]
                                pril_dict = {'пріл': pril_name}
                                for element in pril_info[end_of_name+1:].split(', '):
                                    pril_dict[element.split('.')[0]] = element.split('.')[1].strip()
                        time_dict[key_].append(list(filter(lambda a: a, [general_dict, pril_dict, other_dict])))
                        settlement[key].append(time_dict)
                        pass
                    elif key_ == 'Дот.' or key_ == 'Дот. т.':
                        value = line_[1].replace('\n', ' ').split('; ')
                        other_dict = None
                        time_dict[key_] = []
                        if len(value) > 1:
                            other = value[-1]
                            other_dict = {'інше': other}
                            value.pop(-1)
                        values = value[0].split(', ')
                        for element in values:
                            el_dict = {}
                            try:
                                key_end = re.search('[псінгорадеужл]{1,4}[.]{1}', element).span()[1]
                                dot_key = re.search('[псінгорадлеуж]{1,4}[.]{1}', element).group()
                            except AttributeError:
                                key_end = 0
                                dot_key = 'п. '
                            element = element[key_end:]
                            patterns = re.findall('[0-9]{1,2}\s[haаm2]{1,2}', element)
                            num_dict = {}
                            for pattern in patterns:
                                num_dict[pattern.split(' ')[1]] = pattern.split(' ')[0]
                            el_dict[dot_key] = num_dict
                            time_dict[key_].append(el_dict)
                        if other_dict:
                            time_dict[key_].append(other_dict)
                        settlement[key].append(time_dict)
                    #  всі решту стрічки
                    else:
                        complex_dict = {}
                        try:
                            value = line_[1].replace('\n', ' ')
                        except IndexError:
                            continue
                        items = value.split(',')
                        flag = True
                        for item in items:
                            if key_ == 'Парох' and flag:# and item.split('.')[0] == 'о':
                                complex_dict["ім'я"] = item
                                flag = False
                            elif key_ == 'Стар.' and flag:
                                complex_dict['Стар.'] = item.split(' ')[0]
                                complex_dict['відстань'] = ' '.join(item.split(' ')[1:])
                                flag = False
                            else:
                                try:
                                    complex_dict[item.split('.')[0]] = item.split('.')[1]
                                except IndexError:
                                    complex_dict['0'] = item
                        time_dict[key_] = complex_dict
                        settlement[key].append(time_dict)
        # додаємо населений пункт в список
        lines.append(settlement)
    lines.pop(0)
    # pprint(lines)
    return lines


if __name__ == '__main__':
    data = parse_(read_file('hodoriv.txt'))
    new_main_dct = {}
    for main_dct in data:
        main_key = list(main_dct.keys())[0]
        inner = {}
        for dct in main_dct[main_key]:
            for key in dct:
                inner[key] = dct[key]
        new_main_dct[main_key] = inner
    with open("hodoriv.json", "w", encoding="utf-8") as file:
        json.dump(new_main_dct, file, indent=4, ensure_ascii=False)
