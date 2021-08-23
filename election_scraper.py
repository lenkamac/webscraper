# import
import requests
from bs4 import BeautifulSoup
import sys
import csv


def check_args(b_url, argv):   # control of the input arguments
    if len(argv) == 3:
        try:
            args_url = argv[1]
            csv_date = argv[2]
            if b_url not in args_url:
                sys.exit("Wrong url for scraping!")
            else:
                return args_url, csv_date
        except ValueError:
            sys.exit("Wrong type of arguments!")
    else:
        sys.exit("Wrong number of arguments!")


def file_csv(file, data):
    with open(f"{file}.csv", mode="w", newline="") as f:
        header = data[0].keys()
        w = csv.DictWriter(f, fieldnames=header)

        try:
            w.writeheader()
            w.writerows(data)
        except csv.Error as e:
            sys.exit(f"CSV Error: {e}")


def get_html(cell_url):  # store website, soup object
    response = requests.get(cell_url)
    print(response.status_code, "waiting ...")
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def clear_text(string):
    # replace \n
    try:
        return int(string.replace("\xa0", ""))
    except ValueError as e:
        sys.exit(f"Problem with value: {e}")


def get_links_info(links, elem_table):
    soup = get_html(links)
    elem_table["registered"] = clear_text(soup.find("td", {"headers": "sa2"})
                                          .text)
    elem_table["envelopes"] = clear_text(soup.find("td", {"headers": "sa3"})
                                         .text)
    elem_table["valid"] = clear_text(soup.find("td", {"headers": "sa6"}).text)

    # parties
    parties_table = soup.find_all("table", {"class": "table"})[1:]
    for table in parties_table:
        parties = table.find_all("tr")[2:]
        for partie in parties:
            partie_name = partie.td.findNext("td").text
            if partie_name == "-":
                continue
            elem_table[partie_name] = partie.td.findNext("td").findNext("td")\
                .text


def get_data(from_url):
    data_list = []
    soup = get_html(from_url)
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all("tr")[2:]
        for row in rows:
            if row.find("td").text == "-":
                continue

            elem_table = dict(code="", location="", registered=0, envelopes=0,
                              valid=0)

            elem_table['code'] = row.find(class_='cislo').find('a').get_text()
            elem_table['location'] = row.find(class_='cislo').findNext(
                'td').get_text()

            links = base_url + row.find("a")["href"]
            get_links_info(links, elem_table)

            data_list.append(elem_table)
    return data_list


if __name__ == '__main__':
    base_url = "https://volby.cz/pls/ps2017nss/"
    url, csv_data = check_args(base_url, sys.argv)
    file_data = get_data(url)
    file_csv(csv_data, file_data)
    print(f'Successful. The output data are stored in {csv_data}.csv')
