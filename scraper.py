import re
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs 
from urllib.parse import urlparse
from urllib.parse import urldefrag

def scraper(url, resp):
    links = extract_next_links(url, resp)
    new_links = [link for link in links if is_valid(link)]
    print(new_links)
    return new_links

def extract_next_links(url, resp):
    # Implementation requred.
    if is_valid(url):
        visited_pages = []
        if 'http' not in url:
            url = get_complete_url_scheme(url)
        response = requests.get(url)
        source_code = response.text
        soup_object = bs(source_code,'lxml')
        for link in soup_object.find_all('a'):
            current_link = link.get('href')
            current_link = urldefrag(current_link).url
            if current_link!='':
                if current_link[0]=="/" and current_link[1].isalnum(): #adding root and scheme since it's missing
                    current_link = get_complete_url_scheme_root(current_link,url)
                elif 'http' not in current_link:
                    current_link = get_complete_url_scheme(current_link)
                if current_link not in visited_pages and check_dead_pages(current_link):
                    visited_pages.append(current_link)
    return visited_pages

def is_valid(url):
    #implement error codes
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|@)$", parsed.path.lower()):
            return False
        if check_valid_domain(parsed):
            return True
        else:
            return False
    except TypeError:
        print ("TypeError for ", parsed)
        raise

def check_valid_domain(parsed):
    possible_domains = ['ics.uci.edu','cs.uci.edu','informatics.uci.edu','stat.uci.edu','today.uci.edu']
    possible_paths = ["*","*","*","*","department/information_computer_sciences/"]
    length_of_domain = len(parsed.netloc.split("."))
    for d in possible_domains:
        if length_of_domain==3 and parsed.netloc.lower() == possible_domains[-1] and possible_paths[-1] in parsed.path.lower():
            return True
        elif parsed.netloc != possible_domains[-1] and d in parsed.netloc.lower():
            return True
    return False

def get_complete_url_scheme_root(current_link,url):
    try:
        parsed = urlparse(url)
        return 'https://'+parsed.netloc+current_link
    except TypeError:
        print ("TypeError for ", parsed)
        raise
def get_complete_url_scheme(current_link):
    if current_link[0:2]=="//":
        return "https:"+current_link
    return "https://"+current_link

def check_dead_pages(current_url):
    try:
        response = requests.get(current_url)
        if response.status_code==200 and response.text!='':
           return True
    except:
        pass
    return False








        


    
