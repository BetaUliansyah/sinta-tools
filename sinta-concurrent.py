import requests
from bs4 import BeautifulSoup
import csv
import re
import concurrent.futures

def sinta_find_lastpage():
    s = requests.Session()
    r = s.get('https://sinta.kemdikbud.go.id/journals?page=1')
    bsoup = BeautifulSoup(r.text, 'html.parser')
    allsmalls = bsoup.find_all("small")
    for small in allsmalls:
        if small.find(text=re.compile("Page 1 of")):
            list = small.text.split()
            return int(list[3])
            break

def sinta_singlepage(page):
    #s = requests.Session()
    r = requests.get('https://sinta.kemdikbud.go.id/journals?page='+ str(page))
    bsoup = BeautifulSoup(r.text, 'html.parser')
    journal_names = bsoup.find_all("div", {"class":"affil-name mb-3"})
    journal_urls = bsoup.find_all("div", {"class":"affil-abbrev"})
    journal_accreditations =  bsoup.find_all("span", {"class":" num-stat accredited"})
    return_value = []
    for i in range(0, len(journal_names)):
        # mencari nama jurnal
        journal_name = journal_names[i].find('a').text.strip()
        
        # mencari URL jurnal
        journal_url = journal_urls[i].find_all('a')[1]['href']

        # mencari akreditasi jurnal
        journal_accreditation = journal_accreditations[i].text.strip()

        # return value
        result_data = [journal_name, journal_url, journal_accreditation]
        with open("sinta-data.csv", mode='a+') as sintacsv_file:
            sintacsv_writer = csv.writer(sintacsv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            sintacsv_writer.writerow(result_data)
        return_value.append(result_data)          
    return return_value
    
if __name__ == "__main__":
    filename = "sinta-data.csv"
    header_row = ['journal_name', 'journal_url', 'journal_accreditation']
    with open(filename, mode='w') as sintacsv_file:
        sintacsv_writer = csv.writer(sintacsv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sintacsv_writer.writerow(header_row)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i in range(1, sinta_find_lastpage()+1):
            futures.append(executor.submit(sinta_singlepage, page=i))
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
