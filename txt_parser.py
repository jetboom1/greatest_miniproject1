from pprint import pprint
from geopy import Nominatim
from geopy.exc import GeocoderUnavailable
from geopy.extra.rate_limiter import RateLimiter
from church_parsing import church_parser
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
        stuff_dict = dict()
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
                    key_ = line_[0].lower()
                    # якщо ключ строчки є школа
                    if key_ == 'шк.' or key_ == 'шк':
                        values = line_[1].replace('\n', ' ').split(';')
                        general_dict = {key_: []}
                        for value in values:
                            school_dict = {}
                            is_other = True
                            if re.search('-кл[,.]', value):
                                school_dict['клас'] = value[re.search('-кл.', value).start()-1]
                                is_other = False
                            if re.search('пол[.,]|укр[.,]', value):
                                school_dict['мова'] = re.search('пол[.,]|укр[.,]', value).group()
                                is_other = False
                            if re.search('діт[.,]', value):
                                child_dict = {}
                                nationalities = re.findall('грк[.,]\s\d{1,3}|лат[.,]\s\d{1,3}|жид[.,]\s\d{1,3}|'
                                                           'інш[.,]\s\d{1,3}', value)
                                for pair in nationalities:
                                    type, quantity = pair.split(' ')
                                    child_dict[type] = quantity
                                if child_dict:
                                    school_dict['діти'] = child_dict
                                else:
                                    quantity = re.search('діт[.,]\s\d{1,3}', value).group().split(' ')[1]
                                    school_dict['діти'] = quantity
                                is_other = False
                            if re.search('жін[.,]|муж[.,]', value):
                                school_dict['тип'] = re.search('жін[.]|муж[.]', value).group()
                                is_other = False
                            if is_other:
                                school_dict['інше'] = value
                            general_dict[key_].append(school_dict)
                        settlement[key].append(general_dict)
                    elif key_ == 'надає':
                        time_dict[key_] = dict()
                        value_x = line_[1].replace('\n', ' ').lstrip()
                        if ',' in value_x or '»' in value_x:
                            time_dict[key_]['тип'] = 'організація'
                        else:
                            time_dict[key_]["тип"] = 'особа'
                        time_dict[key_]['назва'] = value_x
                        settlement[key].append(time_dict)
                    elif key_ == 'душ':
                        values = line_[1].replace('\n', ' ').split(';')
                        other = ''
                        school_dict = {}
                        other_dict = {}
                        is_general_parsed = False
                        pril_dict = {}
                        for elements in values:
                            if elements.strip().startswith('в прил.'):
                                pril_info = elements.strip()[8:]
                                end_of_name = re.search('\s[а-яі]{3}[.:]{1}', pril_info).span()[0]
                                pril_name = pril_info[:end_of_name]
                                pril_dict = {'прил': pril_name}
                                for element in pril_info[end_of_name + 1:].split(', '):
                                    pril_dict[element.split('.')[0]] = element.split('.')[1].strip()
                            elif elements == values[-1] and is_general_parsed == True:
                                if len(values) > 1:
                                    other = values[-1]
                                    other_dict = {'інше': other}
                            else:
                                is_general_parsed = True
                                for element in elements.split(', '):
                                    try:
                                        school_dict[element.split('.')[0]] = element.split('.')[1].strip()
                                    except IndexError:
                                        continue
                        school_dict.update(other_dict)
                        if pril_dict == {}:
                            time_dict[key_] = school_dict
                        else:
                            time_dict[key_] = [school_dict, pril_dict]
                        settlement[key].append(time_dict)
                    elif key_ == 'дот.' or key_ == 'дот. т.':
                        value = line_[1].replace('\n', ' ').split('; ')
                        time_dict[key_] = {}
                        other_dict = None
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
                            time_dict[key_].update(el_dict)
                        if other_dict:
                            time_dict[key_].update(other_dict)
                        settlement[key].append(time_dict)
                    #  всі решту стрічки
                    else:
                        complex_dict = {}
                        try:
                            value = line_[1].replace('\n', ' ')
                        except IndexError:
                            continue
                        items = value.lstrip(' ').split(',')
                        flag = True
                        flag_2 = True
                        for item in items:
                            if key_ == 'парох' and flag:  # and item.split('.')[0] == 'о':
                                if "о." in item:
                                    item_list = item.split(' ')
                                    complex_dict['тип'] = item_list[0]
                                    complex_dict["ім'я"] = item_list[1]
                                    if len(item_list) == 3:
                                        complex_dict['прізвище'] = item_list[2]
                                    flag = False
                            elif key_ == 'завідатель' and flag_2:
                                if "о." in item:
                                    item_list = item.split(' ')
                                    complex_dict['тип'] = item_list[0]
                                    complex_dict["ім'я"] = item_list[1]
                                    if len(item_list) == 3:
                                        complex_dict['прізвище'] = item_list[2]
                                    flag_2 = False
                            elif key_ == 'завідує':
                                complex_dict['парох'] = item
                            elif key_ == 'стар.' and flag:
                                complex_dict['Стар.'] = item.split(' ')[0]
                                complex_dict['відстань'] = ' '.join(item.split(' ')[1:])
                                flag = False
                            else:
                                try:
                                    if item.split('.')[0] == ' ж' or item.split('.')[0] == ' вд' or item.split('.')[
                                        0] == ' бж':
                                        complex_dict['стан'] = item.split('.')[0].lstrip()
                                    else:
                                        complex_dict[item.split('.')[0].lstrip()] = item.split('.')[1]
                                except IndexError:
                                    complex_dict['0'] = item
                        if 'парох' == key_ or 'завідує' == key_ or 'завідатель' == key_:
                            time_dict[key_] = complex_dict
                            if 'персонал' not in stuff_dict.keys():
                                stuff_dict['персонал'] = time_dict
                                settlement[key].append(stuff_dict)
                            else:
                                stuff_dict['персонал'][key_] = time_dict[key_]
                                settlement[key].append(stuff_dict)
                        else:
                            time_dict[key_] = complex_dict
                            settlement[key].append(time_dict)
        # додаємо населений пункт в список
        lines.append(settlement)
    lines.pop(0)
    # pprint(lines)
    return lines


def functionality(data, path_to_json):
    new_main_dct = {}
    result = []
    for main_dct in data:
        main_key = list(main_dct.keys())[0]
        inner = {}
        for dct in main_dct[main_key]:
            for key in dct:
                inner[key] = dct[key]
        new_main_dct[main_key] = inner
        result.append(new_main_dct[main_key])
    with open(path_to_json, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    data1 = parse_(read_file('text/stymilo-kamenets.txt'))
    functionality(data1, "jsons/strymilo-kamenets.json")
    data2 = parse_(read_file('text/hodoriv.txt'))
    functionality(data2, 'jsons/hodoriv.json')
    data3 = parse_(read_file('text/zbarazh.txt'))
    functionality(data3, 'jsons/zbarazh.json')
