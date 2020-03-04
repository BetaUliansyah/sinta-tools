#@Sinta Hunter by beta.uliansyah@pknstan.ac.id
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse 
import json
import re


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
    lastpage = lastpage[0]
    print("Bismillah, lets start srcapping " + lastpage + " pages of Sinta journals")

    # looping halaman Sinta sampai lastpage
    page = 1
    journal_no = 1
    while page < int(lastpage) + 1:
        # development purpose, uncomment two lines following to limit number of pages to be scrapped
        #if page == 2:
        #    break
        
        r = s.get('http://sinta.ristekbrin.go.id/journals?page='+ str(page) +'&sort=impact')
        bsoup = BeautifulSoup(r.text, 'html.parser')
        journals_in_this_page = bsoup.find_all("dl", {"class":"uk-description-list-line"})
        for journal in journals_in_this_page:
            journal_link = journal.find('a')
            journal_info = journal.find('span', attrs={'class' :'index-val-small', 'style': re.compile('color')}) # cari span dengan color apapun
            print(str(journal_no) + ". " + journal_link.text)
            print("   Akreditasi: " + journal_info.text)
            
            r = s.get('http://sinta.ristekbrin.go.id'+journal_link['href'])
            if r.status_code==200:
                bsoup = BeautifulSoup(r.text, 'html.parser')
                # cari <a href="http://journal.unhas.ac.id/index.php/fs/index" ><i class="uk-icon-globe uk-text-primary"></i> Website</a> | 
                journal_urls = bsoup.find_all('a')
                for journal_url in journal_urls:
                    if journal_url.find(text=re.compile("Website")):
                        journal_url = journal_url['href']
                        break
                print("   URL: " + journal_url)
            journal_no = journal_no +1
            
        page = page + 1



# Credits:
# https://stackoverflow.com/questions/11716380/beautifulsoup-extract-text-from-anchor-tag
# https://stackoverflow.com/questions/5815747/beautifulsoup-getting-href
# https://stackoverflow.com/questions/50338108/using-beautifulsoup-in-order-to-find-all-ul-and-li-elements
# https://stackoverflow.com/questions/17246963/how-to-find-all-lis-within-a-specific-ul-class
# https://stackoverflow.com/questions/31958637/beautifulsoup-search-by-text-inside-a-tag
