import requests
from bs4 import BeautifulSoup


rossvyaz_url = 'https://rossvyaz.gov.ru/about/otkrytoe-pravitelstvo/otkrytye-dannee/reestr-otkrytykh-dannykh'
phones_csv_dict = {
    'abc3': 'CSV-ABC-3',
    'abc4': 'CSV-ABC-4',
    'abc8': 'CSV-ABC-8',
    'def': 'CSV-DEF-9',
}
#TODO add local SSL CA from system storage for correct verify
#After that - delete ', verify=False' from requests.get() calls


def get_lists_of_phones(numstype: str = 'def'):
    result_lst = []
    if numstype in phones_csv_dict.keys():
        html_body = requests.get(rossvyaz_url, verify=False).text
        soup_body = BeautifulSoup(html_body, 'lxml')
        phones_csv_url = soup_body.find('a', text=phones_csv_dict.get(numstype)).get('href')
        phones_csv_file = requests.get(phones_csv_url, verify=False).text
        phones_lst = phones_csv_file.split('\n')
        phones_keys = phones_lst.pop(0).split(';')
        for iter_lst in map(lambda s: s.split(';'), phones_lst):
            #TODO Need to add normalizer for numbers in start and end of range columns - leading zeros are missed
            result_lst.append(dict(map(lambda lst, kv: (kv, lst), iter_lst, phones_keys)))
    return result_lst


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
#TODO Need to add normalizer for names of regions in regions_set
#TODO Need to add working FIAS database (think about importing this data from GAR format to ClickHouse and work through it)
#TODO Add links between names of regions and terriroty codes

#Final goal - output of script must be JSON in format:
#{
#    "start_number": "9001400000",
#    "range_length": "5",
#    "operator_name_rossvyaz": "ООО T2 Мобайл",
#    "region_name_rossvyaz": "г. Москва * Московская область",
#    "region_name_fias": "Город Москва",
#    "region_code_fias": "77",
#}
