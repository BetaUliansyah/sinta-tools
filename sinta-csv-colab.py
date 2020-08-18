#@Sinta Hunter by beta.uliansyah@pknstan.ac.id
# this version is suitable to run from Colab or notebook
# data is saved to your Google Drive

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse 
import re
import csv
from datetime import date
from google.colab import drive
drive.mount('/content/drive')

def sinta_lastpage():
    """
    Find last page of Sinta list
    """
    s = requests.Session()
    r = s.get('http://sinta.ristekbrin.go.id/journals')
    bsoup = BeautifulSoup(r.text, 'html.parser')
    lastpage = 1

    if r.status_code==200:
        # mencari halaman terakhir
        for ultag in bsoup.find_all('ul', {'class': 'top-paging'}):
            for litag in ultag.find_all('li'):
                for links in litag.find_all('a', href=True):
                    # parse_qs is not working well in Python 3 at the time I wrote this code. so i use regex
                    # .query or [4], Read: https://docs.python.org/3/library/urllib.parse.html
                    query = urlparse(links['href']).query
                    lastpage = re.compile('page=(\d+)').findall(query)
        lastpage = int(lastpage[0])
    return lastpage

def sinta_readpages(startpage=1, lastpage=sinta_lastpage()):
    # prepare file name with date and write header
    filename = "sinta-data-" + str(date.today()) + ".csv"
    header_row = ['journal_no', 'journal_name', 'journal_accreditation', 'journal_url']
    with open("drive/My Drive/sinta-tools/"+filename, mode='w') as sintacsv_file:
        sintacsv_writer = csv.writer(sintacsv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sintacsv_writer.writerow(header_row)
    print(header_row)

    # looping halaman Sinta dari startpage sampai lastpage
    return_value = []
    currentpage = startpage
    journal_no = (startpage-1) * 9 + 1
    i = 0
    while currentpage < int(lastpage) + 1:
        # development purpose, uncomment two lines following to limit number of pages to be scrapped
        #if page == 620:
        #    break

        # session
        s = requests.Session()
        r = s.get('http://sinta.ristekbrin.go.id/journals?page='+ str(currentpage) +'&sort=impact')
        bsoup = BeautifulSoup(r.text, 'html.parser')
        journals_in_this_page = bsoup.find_all("dl", {"class":"uk-description-list-line"})
        for journal in journals_in_this_page:
            # mencari nama jurnal
            journal_link = journal.find('a')

            #mencari akreditasi
            journal_info = journal.find('span', attrs={'class' :'index-val-small', 'style': re.compile('color')}) # cari span dengan color apapun
            
            # mencari URL jurnal
            r = s.get('http://sinta.ristekbrin.go.id'+journal_link['href'])
            if r.status_code==200:
                jsoup = BeautifulSoup(r.text, 'html.parser')
                # cari <a href="http://journal.unhas.ac.id/index.php/fs/index" ><i class="uk-icon-globe uk-text-primary"></i> Website</a> | 
                
                # mencari URL
                journal_urls = jsoup.find_all('a')
                for journal_url in journal_urls:
                    if journal_url.find(text=re.compile("Website")):
                        journal_url = journal_url['href']
                        break
                #print("   URL: " + journal_url)
                
            # prepare result_data
            result_data = [journal_no, journal_link.text, journal_info.text, journal_url]
            with open(filename, mode='a+') as sintacsv_file:
                sintacsv_writer = csv.writer(sintacsv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                sintacsv_writer.writerow(result_data)
            return_value.append(result_data)
            print(result_data)
            journal_no = journal_no +1
            i += 1
            
        currentpage = currentpage + 1
    return return_value

if __name__ == "__main__":
    sinta_readpages()
    # sinta_readpages(startpage=3, lastpage=4)
    # sinta_readpages(7, 8)




# Credits:
# https://stackoverflow.com/questions/11716380/beautifulsoup-extract-text-from-anchor-tag
# https://stackoverflow.com/questions/5815747/beautifulsoup-getting-href
# https://stackoverflow.com/questions/50338108/using-beautifulsoup-in-order-to-find-all-ul-and-li-elements
# https://stackoverflow.com/questions/17246963/how-to-find-all-lis-within-a-specific-ul-class
# https://stackoverflow.com/questions/31958637/beautifulsoup-search-by-text-inside-a-tag
