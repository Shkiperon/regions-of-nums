import requests
import re
from bs4 import BeautifulSoup


mincifri_base_url = 'https://digital.gov.ru/ru/activity/govservices/20/'
fns_base_url = 'https://www.nalog.ru/'
phones_csv_dict = {
    'abc3': 'https://digital.gov.ru/uploaded/files/abc-3xx',
    'abc4': 'https://digital.gov.ru/uploaded/files/abc-4xx',
    'abc8': 'https://digital.gov.ru/uploaded/files/abc-8xx',
    'def': 'https://digital.gov.ru/uploaded/files/def-9xx',
}


def get_soup_body(base_url: str):
    html_body = requests.get(base_url).text
    return BeautifulSoup(html_body, 'html.parser')


def get_lists_of_phones(numstype: str = 'def'):
    result_lst = []
    phones_csv_url = ''
    if numstype in phones_csv_dict.keys():
        soup_body = get_soup_body(mincifri_base_url)
        search_regex = re.escape(phones_csv_dict.get(numstype)) + r'[0-3][1-9](0[1-9]|1[1-2])20[2-3][0-9]\.csv'
        for phones_csv_tag in soup_body.find_all('a', string='csv'):
            if re.match(search_regex, phones_csv_tag.get('href')):
                phones_csv_url = phones_csv_tag.get('href')
                break
        phones_csv_file = requests.get(phones_csv_url).text
        phones_lst = phones_csv_file.split('\n')
        phones_keys = phones_lst.pop(0).split(';')
        for iter_lst in map(lambda s: s.split(';'), phones_lst):
            result_lst.append(dict(map(lambda lst, kv: (kv, lst), iter_lst, phones_keys)))
    return result_lst


def get_list_of_regions():
    soup_body = get_soup_body(fns_base_url)
    options = soup_body.find('select', {'id': 'ctl00_ctl00_ddlRegion_firstpage'})
    for i in options.find_all('option'):
        region_code, region_name = re.split(r' ', i.string, maxsplit=1)
        if re.match(r'\d{2}', region_code):
            print(f"Code: '{region_code}'; Name: '{region_name.strip().replace('  ', ' ')}'")
        else:
            print(f'Bad region code: {region_code}')


def_phones_lst = get_lists_of_phones()
pref_set = set()
oper_set = set()
region_set = set()
for phone_dict in def_phones_lst:
    pref_set.add(phone_dict['АВС/ DEF'])
    oper_set.add(phone_dict['Оператор'])
    region_set.add(phone_dict['Регион'])
print(pref_set)
print(len(pref_set))
print('--------')
print(oper_set)
print(len(oper_set))
print('--------')
print(region_set)
print(len(region_set))
print('--------')
get_list_of_regions()
#TODO Need to add normalizer for names of regions in regions_set
#TODO Need to add working FIAS database (think about importing this data from GAR format to ClickHouse and work through it)
#TODO Add links between names of regions and terriroty codes

#Final goal - output of script must be JSON in format:
#{
#    "start_number": "9001400000",
#    "range_length": "5",
#    "operator_name_mincifri": "ООО T2 Мобайл",
#    "region_name_mincifri": "г. Москва * Московская область",
#    "region_name_fns": "Город Москва",
#    "region_code_fns": "77",
#}
