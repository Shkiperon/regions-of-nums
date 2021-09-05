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
    if numstype not in phones_csv_dict.keys():
        return (False, {})
    html_body = requests.get(rossvyaz_url, verify=False).text
    soup_body = BeautifulSoup(html_body, 'lxml')
    phones_csv_url = soup_body.find('a', text=phones_csv_dict.get(numstype)).get('href')
    phones_csv_file = requests.get(phones_csv_url, verify=False).text
    phones_csv_file.pop(0)
    print(phones_csv_file)
    return (True, {})

get_lists_of_phones()
