import re
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs 
from urllib.parse import urlparse
from urllib.parse import urldefrag
from nltk.corpus import stopwords

def scraper(url, resp):
    links = extract_next_links(url, resp)
    new_links = [link for link in links if is_valid(link)]
    print(new_links)
    return new_links

def extract_next_links(url, resp):
    # Implementation requred.
    if is_valid(url) and check_low_high_content(url):
        new_pages = []
        if 'http' not in url:
            url = get_complete_url_scheme(url)
        response = requests.get(url)
        source_code = response.text
        soup_object = bs(source_code,'lxml')
        for link in soup_object.find_all('a'):
            current_link = link.get('href')
            current_link = urldefrag(current_link).url
            if len(current_link)>2:
                if current_link[0] == "/" and current_link[1].isalnum(): #adding root and scheme since it's missing
                    current_link = get_complete_url_scheme_root(current_link,url)
                elif 'http' not in current_link:
                    current_link = get_complete_url_scheme(current_link)
                if check_dead_pages(current_link) and is_valid(current_link) and check_low_high_content(current_link) and get_unique_url(current_link):
                    new_pages.append(current_link)
    return new_pages

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
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False
        if check_valid_domain(parsed):
            return True
        else:
            return False
    except TypeError:
        print ("TypeError for ", parsed)
        raise

def check_valid_domain(parsed):
    possible_domains = ['ics.uci.edu', 'cs.uci.edu', 'informatics.uci.edu', 'stat.uci.edu', 'today.uci.edu']
    possible_paths = ["*","*","*","*","department/information_computer_sciences/"]
    length_of_domain = len(parsed.netloc.split("."))
    for d in possible_domains:
        if length_of_domain == 3 and parsed.netloc.lower() == possible_domains[-1] and possible_paths[-1] in parsed.path.lower():
            return True
        elif parsed.netloc != possible_domains[-1] and d in parsed.netloc.lower():
            return True
    return False

def get_complete_url_scheme_root(current_link,url):
    try:
        parsed = urlparse(url)
        return 'https://' + parsed.netloc + current_link
    except TypeError:
        print ("TypeError for ", parsed)
        raise

def get_complete_url_scheme(current_link):
    if current_link[0:2] == "//":
        return "https:" + current_link
    return "https://" + current_link

def check_dead_pages(current_url):
    try:
        response = requests.get(current_url)
        if response.status_code == 200 and response.text != '':
           return True
    except:
        pass
    return False

def get_unique_url(url):
    url_file = open("unique_url.txt", "a+")
    url_file.seek(0)
    lines = url_file.read().strip(" ").split("\n")
    if lines == ['']:
        url_file.write(url)
        return True
    lines.sort()
    common = common_stuff(lines)
    lines = same_max(common, lines)
    blocked_urls = open("blocked.txt", "a+")
    blocked_urls.seek(0)
    lines2 = blocked_urls.readlines()
    blocked_urls.close()
    lines2.sort()
    block_comm = common_stuff(lines2)
    lines2 = same_max(block_comm, lines2)
    temp = False
    for url_blocked in lines2:
        if url_blocked in url:
            temp = True
    if url not in lines and temp == False:
        url_file.write('\n'+ url)
        return True
    else:
        return False
    url_file.close()

def common_stuff(lst):
    common = []
    for urls in range(len(lst)-1):
        for l in range(min(len(lst[urls]), len(lst[urls+1]))):
            try:
                if lst[urls][l] == lst[urls+1][l]:
                    common[urls] += lst[urls][l]
            except IndexError:
                pass
    return common

def same_max(common,lst):
    count = 0
    for com in range(len(common)-1):
        if common[com] == common[com+1]:
            count += 1
        else:
            count = 0
        if count >= 9:
            blocked_urls = open("blocked.txt","a+")
            if blocked_urls.read().strip(" ").split("\n")==['']:
                blocked_urls.write(lst[com])
                blocked_urls.close()
            else:
                blocked_urls.write("\n"+lst[com])
                blocked_urls.close()
                lst = lst[:com-count]  #removes pages from com to com-count
                count = 0
    return lst


def get_page_tokens(current_url):
    res = requests.get(current_url)
    html_page = res.text
    soup = bs(html_page, 'lxml')
    text = soup.find_all(text=True)
    content = ''
    black_list = [
    '[document]',
    'noscript',
    'header',
    'html',
    'meta',
    'head', 
    'input',
    'script',
    ]
    for token in text:
        if token.parent.name not in black_list:
            content += '{} '.format(token)
    tokens = computeWordFrequencies(content)
    tok_file = open("unique_toke.txt", "w+")
    tok_file.seek(0)
    lines = tok_file.readlines()
    full_line  = " "
    for line in lines:
        full_line += line.strip("\n").split(" ")[0]+" "
    temp_lines = lines
    for token in tokens:
        if token[0] in full_line:
            for line in range(len(lines)):
                if lines[line].strip("\n").split(" ")[0] == token[0]:
                    temp_lines[line] = token[0]+" "+str(token[1]+temp_lines[line].split(" ")[1])
        else:
            temp_lines.append(token[0]+" "+token[1])
    for line in temp_lines:
        tok_file.seek(0)
        tok_file.write(line[0]+" "+line[1] +"\n")
    tok_file.close()
    max_token = open("max_token.txt","w+")
    max_tokens_so_far = max_token.readlines()
    if max_tokens_so_far<len(content):
        max_token.seek(0)
        max_token.write(len(content))
    fifty_most_common()
    return tokens

def fifty_most_common():
    tok_file = open("unique_toke.txt", "r")
    lines = tok_file.readlines()
    tok_file.close()
    list_tup_token = []
    for line in lines:
        list_tup_token.append(tuple(line.split(" ")[0],line.split(" ")[1]))
    list_tup_token.sort(key=lambda x: x[1])
    top_50 = open("top_fifty.txt","w")
    for i in range(50):
        top_50.write(list_tup_token[i])
    

def computeWordFrequencies(token):
    toke = []
    count = []
    def freq(tok):
        return (tok,count[toke.index(tok)])
    for t in range(len(token)):
        if token[t] not in toke:
            toke.append(token[t])
            count.append(1)
        else:
            count[toke.index(token[t])]+=1
    return tuple(map(freq,toke))

def check_low_high_content(current_link):
    res = requests.get(current_link)
    html_page = res.text
    soup = bs(html_page, 'lxml')
    text = soup.find_all(text=True)

    content = ''
    blacklist = [
        '[document]',
        'noscript',
        'header',
        'html',
        'meta',
        'head', 
        'input',
        'script',
    ]
    for t in text:
        if t.parent.name not in blacklist:
            content += '{} '.format(t)
    tokens = re.findall('[a-z0-9]+',content.lower())
    stop_words = set(stopwords.words('english'))
    tokens = [w for w in tokens if not w in stop_words]
    if 300<=len(tokens)<=3000:
        return True
    return False

