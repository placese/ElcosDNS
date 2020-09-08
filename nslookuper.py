import os
import pandas as pd
import csv
import re

PATH = '/home/plvc73/Downloads/Telegram Desktop/DNS 26-04-2020.xlsx'

first_sheet = pd.read_excel(PATH, sheet_name='27')
second_sheet = pd.read_excel(PATH, sheet_name='198')
test_sheet = pd.read_excel(PATH, sheet_name='test')

# patternNX = re.compile('NXDOMAIN')
# patternSF = re.compile('SERVFAIL')
# patternNA = re.compile('No answer')
# patternND = re.compile('not found')
# patternFL = re.compile('failure')
# NXDOMAIN  - Свободен
# SERVFAIL  - Ошибка подключения
# No answer - Нет ответа


def get_ns(sheet, saveFile):
    column_name = 'domain'
    sheet_list = sheet[column_name].tolist()
    result = []
    for i in sheet_list:
        # os.system(f'dig +short +noidnin +noidnout NS {i} ')
        out = os.popen(f'dig +short +noidnin +noidnout NS {i} ').read()
        print(out)
        if out == '':
            # os.system(f'nslookup -type=NS {i}')
            out = os.popen(f'nslookup -type=NS {i}').read()
            print(out)
            while True:
                if patternNX.findall(out) == ['NXDOMAIN']:
                    out = 'NXDOMAIN - Свободен'
                    break
                if patternSF.findall(out) == ['SERVFAIL']:
                    out = 'SERVFAIL  - Ошибка подключения'
                    break
                if patternNA.findall(out) == ['No answer']:
                    out = 'No answer - Нет ответа'
                    break
                if patternND.findall(out) == ['not found']:
                    out = 'not found'
                    break
                if patternFL.findall(out) == ['failure']:
                    out = 'failure'
                    break
                break

        result.append({'Домен': i,
                       'Name server': out.replace('\n', ', ')})
    save_file(result, saveFile)
    return result


def save_file(items, saveFile):
    with open(saveFile, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Домен', 'Name server'])
        for i in items:
            domain = i.get('Домен')
            ns = i.get('Name server')
            writer.writerow([domain, ns])


if __name__ == '__main__':
    # get_ns(test_sheet, 'test.csv')
    get_ns(first_sheet, '27.csv')
    get_ns()
