from pprint import pprint
from geopy import Nominatim
from geopy.extra.rate_limiter import RateLimiter


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
    except AttributeError:
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
                    time_dict_1 = {}
                    # на випадок якщо більше ніж одна церква в селі
                    iterator = 1
                    for church in ', '.join(value).replace('\n', ' ').split('; '):
                        church = church.split(', ')
                        time_dict_1[f'церква_{iterator}'] = church
                        iterator += 1
                    settlement[key] = [header(head[1].split()[0], head[0].split()[0], key)]
                    settlement[key].append(time_dict_1)
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
                    # elif key_ == 'Душ' and key == 'ХОДОРІВ; М-ко':
                    #     value = line_[1].replace('\n', ' ')
                    #     other = value.split
                    #  всі решту стрічки
                    else:
                        complex_dict = {}
                        value = line_[1].replace('\n', ' ')
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
    return lines

if __name__ == '__main__':
    file_string = read_file('text/hodoriv.txt')
    parsed = parse_(file_string)
    pass