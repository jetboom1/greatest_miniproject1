from pprint import pprint
import json


def church_parser(text):
    churches = {"церкви": []}
    for row in text:
        if 'ц.' in row:
            words = row.split(',')
            try:
                name = words[0][4:]
            except IndexError:
                name = ''
            try:
                typpe = (words[2].split('.')[0] + '.')[1:]
            except IndexError:
                typpe = ''
            for i in range(10):
                if str(i) in row:
                    try:
                        year = words[2].split('.')[1]
                    except IndexError:
                        year = ''
                else:
                    year = ''
            church = {
                "назва": name,
                "тип": typpe,
                "рік": year[1:]
            }
            for i in range(10):
                if str(i) in row[-20:]:
                    try:
                        key_for_year_2 = words[3][1:4] + '.'
                        year_2 = words[3][6:]
                        church[key_for_year_2] = year_2
                    except IndexError:
                        pass
                else:
                    year = ''

            if "»" in row:
                index_dn_start = row.rfind('»') + 1
                index_dn_end = row.rfind('«')
                church["Дн."] = row[index_dn_start:index_dn_end]

            if "будується" or 'мурується' or 'недокінчена' in row:
                church['тип'] = church['тип'].replace('\n', ' ')
            if 'дер.' in row:
                church['тип'] = 'дер.'
            church_final = {}
            for key in church:
                if church[key] != '':
                    church_final[key] = church[key]
            churches['церкви'].append(church_final)
        # pprint(churches)
    return churches
