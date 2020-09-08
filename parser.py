import parser
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
import pandas as pd
import re
import csv
import os

PATH = '/home/plvc73/Downloads/Telegram Desktop/DNS 26-04-2020.xlsx'

first_sheet = pd.read_excel(PATH, sheet_name='27')
second_sheet = pd.read_excel(PATH, sheet_name='198')
test_sheet = pd.read_excel(PATH, sheet_name='test')

HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
           'accept': '*/*'}

R_AND_D = 'REGISTERED, DELEGATED'
DELEGATED = 'REGISTERED, DELEGATED, VERIFIED'
NOT_DELEGATED = 'REGISTERED, NOT DELEGATED, VERIFIED'
NO_ENTRIES = 'No entries'
NO_MATCH = 'No match'
UNVERIFIED = 'REGISTERED, DELEGATED, UNVERIFIED'
pattern_state = re.compile('state')


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html, domain):
    result = {}
    soup = BeautifulSoup(html, 'html.parser')
    info = soup.find('pre', class_='raw-domain-info-pre')
    info = str(info)
    result.update({'Домен': domain})
    while True:
        if re.compile('Domain Name').findall(info) == ['Domain Name']:
            out = os.popen(f'dig +short +noidnin +noidnout NS {domain} ').read()
            print(out)
            result.update({'Name server': out.replace('\n', ' ')})
            break
        if re.compile(NO_ENTRIES).findall(info) == [NO_ENTRIES] or re.compile(NO_MATCH).findall(info) == [NO_MATCH]:
            result.update({'Статус': 'Free'})
            break
        if pattern_state.findall(info) == ['state']:
            if re.compile(DELEGATED).findall(info) == [DELEGATED]:
                out = os.popen(f'dig +short +noidnin +noidnout NS {domain} ').read()
                print(out)
                result.update({'Name server': out.replace('\n', ' '),
                    'Статус': DELEGATED})
                break
            if re.compile(R_AND_D).findall(info) == [R_AND_D]:
                out = os.popen(f'dig +short +noidnin +noidnout NS {domain} ').read()
                print(out)
                result.update({'Name server': out.replace('\n', ' '),
                               'Статус': R_AND_D})
                break
            if re.compile(NOT_DELEGATED).findall(info) == [NOT_DELEGATED]:
                result.update({'Статус': NOT_DELEGATED})
                break
            if re.compile(UNVERIFIED).findall(info) == [UNVERIFIED]:
                result.update({'Статус': UNVERIFIED})
        break
    print(result)
    return result


def save_file(items, saveFile):
    with open(saveFile, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(['Домен', 'Name server', 'Статус'])
        for i in items:
            domain = i.get('Домен')
            ns = i.get('Name server')
            status = i.get('Статус')
            writer.writerow([domain, ns, status])


def parse(sheet, saveFile):
    column_name = 'domain'
    sheet_list = sheet[column_name].tolist()
    result = []
    for i in sheet_list:
        domain = i
        url = f'https://whois.ru/{domain}'
        html = get_html(url)
        if html.status_code == 200:
            result.append(get_content(html.text, domain))
        else:
            raise Exception("error")
    save_file(result, saveFile)


if __name__ == '__main__':
    # parse(first_sheet, '27.csv')
    parse(second_sheet, '198.csv')
