import os.path
import string
import sys
import time
from itertools import product
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import date
from tqdm import tqdm


def payload_maker(response, page, search_type, fn=''):
    """generates payloads for all post requests. Modifies payload based on
    the function of the request (search), the results returned for each
    search (page), and whether or not a first name is included (fn)"""

    soup = bs(response, 'lxml')
    vs = soup.find("input", {"id": "__VIEWSTATE"}).attrs['value']
    vs_gen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"}).attrs['value']
    vs_val = soup.find("input", {"id": "__EVENTVALIDATION"}).attrs['value']
    data = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": vs,
        "__VIEWSTATEGENERATOR": vs_gen,
        "__EVENTVALIDATION": vs_val,
        }

    if page == "sec":
        data['ctl00$LocatorPublicPageContent$btnAccept'] = "Agree and " \
                                                           "Proceed to Search"

    elif page == "next":
        data["__EVENTTARGET"] = "ctl00$LocatorPublicPageContent$gvGridView",
        data["__EVENTARGUMENT"] = "Page$Next",
        data["__VIEWSTATEENCRYPTED"] = ""

    else:
        data['ctl00$LocatorPublicPageContent$txtCDCNumber'] = ''
        data['ctl00$LocatorPublicPageContent$txtLastName'] = search_type
        data['ctl00$LocatorPublicPageContent$txtFirstName'] = fn
        data['ctl00$LocatorPublicPageContent$txtMiddleName'] = ''
        data['ctl00$LocatorPublicPageContent$btnSearch'] = 'Search for Inmate'

    return data


def results(response):
    """parses request content with beautiful soup and checks to see if a
    tbale has loaded (found), if the search returned multiple pages of
    results (next) and if it returned a truncated list of requests (limit)
    and returns them as a tuple of 3 binaries"""

    soup = bs(response, 'lxml')

    dframe = soup.find(
        'table',
        {'id': 'LocatorPublicPageContent_gvGridView'}
        )
    if dframe is None:
        found = 0
    else:
        found = 1

    button = soup.find(
        'a', {'href': "javascript:__doPostBack('ctl00$LocatorPublicPageContent$gvGridView','Page$Next')"}
        )
    if button is None:  # indicates only one page of results
        page = -1
    else:  # 3 indacates multiple pages of results
        page = -3

    #  Testing to see if there are more than 1000 resuslts
    warning = soup.find('span', {'class': 'alert alert-success'})
    if warning is None:
        limit = 0
    else:
        limit = 1

    return found, page, limit


def parse(reponse, end):
    """pasrses content with beautiful soup and extracts table information to
    send to the scrape function"""

    try:
        soup = bs(reponse, 'lxml')
        dframe = soup.find('table', {'id':
                                       'LocatorPublicPageContent_gvGridView'})
        rows = dframe.find_all('tr')
        for row in rows[1:end]:
            cols = row.find_all('td')
            name = cols[0].text
            num = cols[1].text
            age = cols[2].text
            parol = cols[3].text
            fac = cols[4].text.strip()
            # print(name)
            # print(num)
            # print(age)
            # print(parol)
            # print(fac)
            scrape(
                name,
                num,
                age,
                parol,
                fac
                )
    except AttributeError as e:
        # print(e)
        return False


def next_page(response):
    """parses content with BS and searches for a "next" button. Returns
    False if no button is present, and True if present"""

    soup = bs(response, 'lxml')
    button = soup.find('a', {'href': "javascript:__doPostBack("
                             "'ctl00$LocatorPublicPageContent$gvGridView','Page$Next')"})
    if button is None:
        return 0
    else:
        return 1


def scrape(name, num, age, parol, fac):
    """creates dictionary with parsed table data and appends to global list
    DETAILS"""

    d = {
        "name": name,
        "num": num,
        'age': age,
        'parol': parol,
        'fac': fac
        }
    # Appending Details To Dictionaries
    DETAILS.append(d)


def parse_block(content, pages, r):
    """parses and scrapes data then checks to see if next is True or False.
    If there are multiple pages (indicated by next_page() output, it sends a
    "next"
    post request, parses and sccrapes the data until next returns false"""
    parse(content, pages)
    while next_page(content):
        time.sleep(.5)
        payload = payload_maker(r.content, 'next', "")
        url3 = 'https://inmatelocator.cdcr.ca.gov/Results.aspx'
        r = requests.post(url3, payload)
        content = r.content
        parse(content, pages)


DETAILS = []  # holds scraped information to be exported to pandas df


def main():
    art = """ 
 ___________  _____ ______                                        
/  __ \  _  \/  __ \| ___ \                                       
| /  \/ | | || /  \/| |_/ /                                       
| |   | | | || |    |    /                                        
| \__/\ |/ / | \__/\| |\ \                                        
 \____/___/   \____/\_| \_|                                       
                                                                  
                                                                  
     _               _____ _____ ______  ___  ______ ___________  
    | |             /  ___/  __ \| ___ \/ _ \ | ___ \  ___| ___ \ 
 ___| | ___   _ ___ \ `--.| /  \/| |_/ / /_\ \| |_/ / |__ | |_/ / 
/ __| |/ / | | / __| `--. \ |    |    /|  _  ||  __/|  __||    /  
\__ \   <| |_| \__ \/\__/ / \__/\| |\ \| | | || |   | |___| |\ \  
|___/_|\_\\__, |___/\____/ \____/\_| \_\_| |_/\_|   \____/\_| \_| 
           __/ |                                                  
          |___/                                                   
 _   _    ___                                                     
| | | |  /   |                                                    
| | | | / /| |                                                    
| | | |/ /_| |                                                    
\ \_/ /\___  |                                                    
 \___/     |_/ ~ By VoidTrauma                                                    
                   """
    print(art)
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    searches = [a + b for a, b in
                product(string.ascii_lowercase, repeat=2)]

    print("Making Connections...")
    base_url = "https://inmatelocator.cdcr.ca.gov"
    url1 = f"{base_url}/search.aspx"
    url2 = f"{base_url}/default.aspx"

    #  Initial request to begin session and navigate terms and conditions
    with requests.session() as s:
        r1 = s.get(url1)
        payload = payload_maker(r1.content, 'sec', 'none')
        r2 = s.post(url2, payload)

    """loops two all two alphabet character combinations sending search 
    requests, and scraping results is present. 1000+ results are truncated by 
    the  website, so in that event (flagged by maxlimit), it generates a new 
    list  of character combinations that begin with the previous dyad followed 
    by  each letter of the alphabet. If maxlimit is flagged again, a new loop is 
    created that attempts the three character last name search with a 1 
    character first name search"""
    time.sleep(5)
    print("Connection Secure...")
    print("Collecting Data...")
    for search in tqdm(searches):
        current = searches.index(search)
        payload = payload_maker(r2.content, 'find', search)
        r = s.post(url1, payload)
        content = r.content
        table, pages, maxlimit = results(content)
        # print(table, pages, maxlimit)
        if table is False:
            continue

        if maxlimit:  # results found more than 1000 results
            accu_search = [search + x for x in string.ascii_lowercase]
            for acs in accu_search:
                # print(acs)
                payload = payload_maker(r2.content, 'find', acs)
                r = s.post(url1, payload)
                content = r.content
                table, pages, maxlimit = results(content)
                # print(table, pages, maxlimit)
                if maxlimit:  # results found more than 1000 results
                    fnames = list(string.ascii_lowercase)
                    for f in fnames:
                        # print(f, acs)
                        payload = payload_maker(r2.content, 'find', acs, fn=f)
                        r = s.post(url1, payload)
                        content = r.content
                        table, pages, maxlimit = results(content)
                        # print(table, pages, maxlimit)
                        parse_block(content, pages, r)
                    continue

                parse_block(content, pages, r)

        parse_block(content, pages, r)
        df = pd.DataFrame(DETAILS)
        file_name = f'data/cdcr_roster_{str(date.today())}.csv'
        df.to_csv(os.path.join(os.getcwd(), file_name))
    print("Roster Complete")
    sys.exit()


if __name__ == '__main__':
    main()
