import sys
import requests
import re
import json
from bs4 import BeautifulSoup


mincifri_base_url = 'https://digital.gov.ru/ru/activity/govservices/20/'
fns_base_url = 'https://www.nalog.gov.ru/'
phones_csv_dict = {
    'abc3': r'https://digital\.gov\.ru/uploaded/files/(abc|avs)-3xx_[a-zA-Z]+\.csv',
    'abc4': r'https://digital\.gov\.ru/uploaded/files/(abc|avs)-4xx_[a-zA-Z]+\.csv',
    'abc8': r'https://digital\.gov\.ru/uploaded/files/(abc|avs)-8xx_[a-zA-Z]+\.csv',
    'def': r'https://digital\.gov\.ru/uploaded/files/def-9xx_[a-zA-Z]+\.csv',
}
dict_of_regions_normalizer_path = './regions_normalizer.json'
try:
    with open(dict_of_regions_normalizer_path) as f:
        dict_of_regions_normalizer = json.load(f)
except IOError:
    dict_of_regions_normalizer = {}
    print('No saved file with. It will be long day :-(')


def get_soup_body(base_url: str):
    html_body = requests.get(base_url).text
    return BeautifulSoup(html_body, 'html.parser')


def get_lists_of_phones(numstype: str = 'def'):
    result_lst = []
    phones_csv_url = ''
    if numstype in phones_csv_dict.keys():
        soup_body = get_soup_body(mincifri_base_url)
        search_regex = phones_csv_dict.get(numstype)
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
    regions_dict = {}
    regions_names = []
    regions_codes = []
    soup_body = get_soup_body(fns_base_url)
    options = soup_body.find('select', {'id': 'ctl00_ctl00_ddlRegion_firstpage'})
    for i in options.find_all('option'):
        region_code, region_name = re.split(r' ', i.string, maxsplit=1)
        if re.match(r'\d{2}', region_code):
            region_clear_name = region_name.strip().replace('  ', ' ')
            regions_names.append({region_clear_name: region_code})
            regions_codes.append({region_code: region_clear_name})
        else:
            print(f'Bad region code: {region_code}')
    regions_dict.update({'regions_names': regions_names})
    regions_dict.update({'regions_codes': regions_codes})
    print(f'{regions_dict}')
    return regions_dict


def_phones_lst = get_lists_of_phones()
region_set = set()
for phone_dict in def_phones_lst:
    region_set.add(phone_dict['Регион'])
result_dict = get_list_of_regions()
region_list_from_fns = result_dict.get('regions_names')
for region_name_mincifri in region_set:
    if region_name_mincifri not in dict_of_regions_normalizer.keys() and region_name_mincifri not in region_list_from_fns:
        try:
            #TODO Change filling algorithm
            region_int_code = int(input(f"Please enter region code for '{region_name_mincifri}': "))
            region_code = f'{region_int_code:02d}'
            region_dict_from_result = result_dict.get(region_code, None)
            updated_list = region_dict_from_result.get('region_names_mincifri_list', [])
            updated_list.append(region_name_mincifri)
            region_dict_from_result.update({'region_names_mincifri_list': updated_list})
            result_dict.update({region_code: region_dict_from_result})
            dict_of_regions_normalizer.update({region_name_mincifri: region_code})
        except ValueError:
            print('Bad region code. Sorry, but we cannot do next steps')
            sys.exit(1)


#TODO Need to add normalizer for names of regions in regions_set
#TODO Add search of region name in region_list_from_fns to decrease number of questions to user

#Final goal - output of script must be JSON in format:
#{
#   ......
#   "77": [{
#           "start_number": "9001400000",
#           "range_length": "5",
#           "operator_name_mincifri": "ООО T2 Мобайл",
#           "region_name_mincifri": "г. Москва * Московская область",
#           "region_name_fns": "Город Москва"
#       },...]
#   ......
#}
