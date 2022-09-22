import csv


def open_scv(file_name: str) -> list:
    with open(f'{file_name}', "r") as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"', encoding='UTF-8')
        return [row for row in reader]


with open(f'db\\companies_db - 2022-09-19.csv', "r") as fp:
    try:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        for row in reader:
            company_name = row[0]
            if company_name.count(',') == 1:
                title = company_name.split(',')
                name = title[0].split('·')[0]
                print(company_name)
    except:pass
