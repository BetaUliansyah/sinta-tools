import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from aiohttp_retry import RetryClient
from async_retrying import retry


def parse_sinta(html):
  bsoup = BeautifulSoup(html, 'html.parser')
  journal_names = bsoup.find_all("div", {"class":"affil-name mb-3"})
  journal_urls = bsoup.find_all("div", {"class":"affil-abbrev"})
  journal_accreditations =  bsoup.find_all("span", {"class": "num-stat accredited"})
  return_value = pd.DataFrame(columns=['journal_name', 'journal_url', 'journal_accreditation'])
  for i in range(0, len(journal_names)):
      # mencari nama jurnal
      journal_name = journal_names[i].find('a').text.strip()
      
      # mencari URL jurnal
      journal_url = journal_urls[i].find_all('a')[1]['href']

      # mencari akreditasi jurnal
      journal_accreditation = journal_accreditations[i].text.strip()

      # return value
      result_data = {
          'journal_name': [journal_name], 
          'journal_url': [journal_url], 
          'journal_accreditation': [journal_accreditation]
      }
      return_value = pd.concat([return_value, pd.DataFrame(result_data)])
  return return_value

async def fetch(url):
    #statuses = {x for x in range(100, 600)}
    #statuses.remove(200)
    #statuses.remove(429)
    async with aiohttp.ClientSession(trust_env = True) as session:
        retry_client = RetryClient(session)
        async with retry_client.get(url) as response:
            return await response.text()

async def main():
    urls = []
    for i in range (1, 808):
      urls.append('https://sinta.kemdikbud.go.id/journals?page='+str(i))
    tasks = [asyncio.create_task(fetch(url)) for url in urls]
    pages = await asyncio.gather(*tasks)
    # do something with the scraped pages
    sintadf = pd.DataFrame(columns=['journal_name', 'journal_url', 'journal_accreditation'])
    for page in pages:
      sintadf = pd.concat([sintadf, pd.DataFrame(parse_sinta(page))])
    return sintadf

#asyncio.run(main())
sintadf = await main()
sintadf.to_csv('sinta-aiohttp.csv')

# credits: https://github.com/inyutin/aiohttp_retry
# https://stackoverflow.com/questions/56152651/how-to-retry-async-aiohttp-requests-depending-on-the-status-code
# when tested on April 27, 2023, it takes 1:24 minutes, producing 812 KB file with 8071 data rows.
