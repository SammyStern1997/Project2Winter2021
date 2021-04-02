#################################
##### Name: Sam Stern
##### Uniqname: sternsam
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
import time
import secrets as secrets

BASE_URL = 'https://www.nps.gov'
COURSES_PATH = '/Desktop/507/Project2Winter2021'
CACHE_FILE_NAME = 'cacheSI_Scrape.json'
CACHE_FILE_NAME_API = "cache.json"
CACHE_DICT = {}

headers = {'User-Agent': 'UMSI 507 Course Project - Python Web Scraping','From': 'sternsams@umich.edu','Course-Info': 'https://www.si.umich.edu/programs/courses/507'}

def load_cache():
    '''Load cache from cache file for api pull
    
    Parameters
    ---------
    None
    
    Returns
    -------
    dict
        cache if it exists, empty cache otherwise.
    '''

    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def load_cache_api():
    '''Load cache from cache file for api pull
    
    Parameters
    ---------
    None
    
    Returns
    -------
    dict
        cache if it exists, empty cache otherwise.
    '''

    try:
        cache_file = open(CACHE_FILE_NAME_API, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache):
    '''Save webscraping cache in file named under var CACHE_FILE_NAME
    
    Parameters
    ---------
    cache: dictionary
        json dictionary to save in file
    
    Returns
    -------
    Nothing
    '''

    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def save_cache_api(cache_dict):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILE_NAME_API,"w")
    fw.write(dumped_json_cache)
    fw.close()

def make_url_request_using_cache(url, cache):
    '''Check if cache exists, otherwises fetch data
    
    Parameters
    ---------
    url: string
        The URL for the website
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the data returned from either the cache or the fetch
    '''
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url, headers=headers)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    response = requests.get(baseurl, params)
    results_object = response.json()
    return results_object

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, name, category, address, zipcode, phone):
        self.name = name
        self.category = category
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        return(f"{self.name} ({self.category}): {self.address} {self.zipcode}")

def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    base_url = 'https://www.nps.gov'


    responseDetail = make_url_request_using_cache(base_url, CACHE_DICT)
    soup = BeautifulSoup(responseDetail, 'html.parser')
    state_list = soup.find('ul', class_='dropdown-menu SearchBar-keywordSearch')
    state_list = state_list.find_all('li')

    state_links = {}

    for item in state_list:
        link = item.find('a').get('href')
        name = item.text.strip()
        state_links[name.lower()] = base_url+link

    return state_links

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    #caching site url
    responseDetail = make_url_request_using_cache(site_url, CACHE_DICT)
    soup = BeautifulSoup(responseDetail, 'html.parser')

    try:
        name = soup.find_all("a", class_="Hero-title")[0].text.strip()
    except:
        name = 'no name'

    try:
        category = soup.find_all("span", class_="Hero-designation")[0].text.strip()
    except:
        category = 'no category'
    try:
        city = soup.find_all("span", itemprop="addressLocality")[0].text.strip()
    except:
        city = "no city"
    # state = soup.find_all("span", class_='region')[0].text.strip()
    try:
        state = soup.find_all("span", itemprop='addressRegion')[0].text.strip()
    except:
        state = 'no state'
    address = f"{city}, {state}"

    try:
        zipcode = soup.find_all("span", itemprop='postalCode')[0].text.strip()
    except:
        zipcode = 'no zipcode'
    try:
        phone = soup.find_all("span", class_='tel')[0].text.strip()
    except:
        phone = 'no phone'

    return NationalSite(name, category, address, zipcode, phone)

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    ns_instances = []
    BASE_URL = 'http://www.nps.gov'

    responseDetail = make_url_request_using_cache(state_url, CACHE_DICT)
    soup = BeautifulSoup(responseDetail, 'html.parser')
 
    park_listing_parent = soup.find('ul', id='list_parks')
    park_listing_h3 = park_listing_parent.find_all('h3')

    for park in park_listing_h3:
        link = park.find('a')['href']
        full_link = BASE_URL + link + 'index.htm'
        ns_inst = get_site_instance(full_link)
        ns_instances.append(ns_inst)
    return ns_instances

def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    url = "http://www.mapquestapi.com/search/v2/radius"
    params = {
        'key': secrets.MQ_API_KEY,
        'origin': site_object.zipcode,
        'radius': '10',
        'maxMatches': '10',
        'ambiguities': 'ignore',
        'outFormat': 'json'
    }
    cache = load_cache_api()
    if cache:
        if cache['origin']['postalCode'] == site_object.zipcode:
            print("Using cache")
        else:
            save_cache_api(make_request(url, params))
            print("Fetching")
            cache = load_cache_api()
    else:
        save_cache_api(make_request(url, params))
        print("Fetching")
        cache = load_cache_api()
    return cache

def print_ns(state, ns_sites):
    '''Print out national site inofrmation from a state
    
    Parameters
    ---------
    state: string
        the state instance that is being crawled
    params: ns_sites
        list of NationalSite instances to print out
    
    Returns
    -------
    Nothing
    '''

    print("----------------------------------")
    print(f"List of national sites in {state.title()}")
    print("----------------------------------")    
    for i in range(len(ns_sites)):
        print(f"[{i+1}] {ns_sites[i].info()}")

    
if __name__ == "__main__":
    # state = input("""Enter a state name (e.g. Michigan, michigan) or "exit": """)
    flag = False
    
    while not flag:
        state = input("""Enter a state name (e.g. Michigan, michigan) or "exit": """)

        if state == "exit":
            quit()

        CACHE_DICT = load_cache()
        state_urls = build_state_url_dict()

        if state.lower() not in state_urls.keys():
            flag=True
            while state.lower() not in state_urls.keys():
                print("[Error] Enter proper state name\n")
                state = input("""Enter a state name (e.g. Michigan, michigan) or "exit": """)
                if state.lower() in state_urls.keys(): break
                if state.lower() =='exit': quit()
        # flag=True
        
        state_link = state_urls[state.lower()]
        ns_sites = get_sites_for_state(state_link)
        print_ns(state, ns_sites)

        step_3_flag = False

        while step_3_flag == False:
            user_num = input("""Choose the number for detail search or "exit" or "back": """)
            if user_num.lower() == 'exit': 
                exit()
            elif user_num.lower() == 'back': 
                step_3_flag = True
                continue
            elif user_num.isnumeric and (int(user_num) < len(ns_sites)+1):
                nearby_places = get_nearby_places(ns_sites[int(user_num)-1])
                print("----------------------------")
                print(f"Places near {ns_sites[int(user_num)-1].name}")
                print("----------------------------")

                for place in nearby_places['searchResults']:
                    name = place['name']
                    category =  place['fields']['group_sic_code_name_ext']
                    address = place['fields']['address']
                    city = place['fields']['city']
                    if (not name) or (name == 'None') or (name == None): city = 'no name'
                    if (not category) or (category == 'None') or (category == None): category = 'no category'
                    if (address == None) or (not address): address = 'no address'
                    if (not city) or (city == 'None') or (city == None): city = 'no city'

                    print(f"- {name} ({category}): {address}, {city}")
            else:
                print(f"[Error] Invalid input\n")
                print(f"-----------------------------")

        if user_num.lower() == 'back': continue




