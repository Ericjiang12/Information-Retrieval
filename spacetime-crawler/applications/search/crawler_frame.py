import logging
from datamodel.search.Yifanj6Yzeng5_datamodel import Yifanj6Yzeng5Link, OneYifanj6Yzeng5UnProcessedLink, add_server_copy, get_downloaded_content
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer, GetterSetter, Getter, ServerTriggers
from lxml import html,etree
import re, os
from time import time
from uuid import uuid4

from urlparse import urlparse, parse_qs
from uuid import uuid4

from bs4 import BeautifulSoup
from urlparse import urljoin

# part of the trap detection algorithms are referenced from https://support.archive-it.org/hc/en-us/articles/208332943-Identify-and-avoid-crawler-traps-

logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"

@Producer(Yifanj6Yzeng5Link)
@GetterSetter(OneYifanj6Yzeng5UnProcessedLink)
@ServerTriggers(add_server_copy, get_downloaded_content)
class CrawlerFrame(IApplication):

    def __init__(self, frame):
        self.starttime = time()
        self.app_id = "Yifanj6Yzeng5"
        self.frame = frame


    def initialize(self):
        self.count = 0
        l = Yifanj6Yzeng5Link("http://www.ics.uci.edu/")
        print l.full_url
        self.frame.add(l)

    def update(self):
        unprocessed_links = self.frame.get_new(OneYifanj6Yzeng5UnProcessedLink)
        if unprocessed_links:
            link = unprocessed_links[0]
            print "Got a link to download:", link.full_url
            downloaded = link.download()
            links = extract_next_links(downloaded)
            for l in links:
                if is_valid(l):
                    self.frame.add(Yifanj6Yzeng5Link(l))

    def shutdown(self):
        print (
            "Time time spent this session: ",
            time() - self.starttime, " seconds.")
    
def extract_next_links(rawDataObj):
    outputLinks = []
    '''
    rawDataObj is an object of type UrlResponse declared at L20-30
    datamodel/search/server_datamodel.py
    the return of this function should be a list of urls in their absolute form
    Validation of link via is_valid function is done later (see line 42).
    It is not required to remove duplicates that have already been downloaded. 
    The frontier takes care of that.
    
    Suggested library: lxml
    '''
    if rawDataObj.is_redirected:
        url = rawDataObj.final_url
    else:
        url = rawDataObj.url

    soup = BeautifulSoup(rawDataObj.content, 'lxml')
    for link in soup.find_all('a'):
        next_url = link.get('href')
        if next_url and next_url[0:7] != "mailto:" and next_url != "#":
            next_url = urljoin(url, next_url).encode('utf-8')
            outputLinks.append(next_url)
    count = len(outputLinks)
    log_file = "log.txt"
    info = []
    try:
        log = open(log_file, 'r')
        info = log.read().splitlines()
        if not info:
            raise IOError
    except IOError:
        log = open(log_file, 'w')
        log.write("total urls crawled: " + str(count)+"\n")
        log.write(rawDataObj.url+" has most out links: " + str(count)+"\n")
    log.close()

    if info:
        log = open(log_file, 'w')
        out_links = int(info[1].split(":")[-1])
        total = int(info[0].split(":")[-1])
        log.write("total urls crawled: " + str(total+count)+"\n")
        if count >= out_links:
            log.write(rawDataObj.url+" has most out links: "+ str(count)+"\n")
        else:
            log.write(info[-1])
        log.close()

    log_file2 = "crawled.txt"
    try:
        log2 = open(log_file2, 'r')
    except IOError:
        log2 = open(log_file2, 'w')
        log2.write("crawled urls\n")
        log2.write("-------------------------------------------------\n")
    log2.close()
    log2 = open(log_file2, 'a')
    log2.write(rawDataObj.url + "\n")
    log2.close()

    return outputLinks

def is_valid(url):
    '''
    Function returns True or False based on whether the url has to be
    downloaded or not.
    Robot rules and duplication rules are checked separately.
    This is a great place to filter out crawler traps.
    '''
    parsed = urlparse(url)
    if parsed.scheme not in set(["http", "https"]):
        return False
    try:
        if re.match("^.*calendar.*$", url) or re.match("r^.*?(/.+?/).*?\1.*$|^.*?/(.+?/)\2.*$", url) \
            or re.match("^.*(/misc|/sites|/all|/themes|/modules|/profiles|/css|/field|/node|/theme){3}.*$", url)\
            or re.match("^.*/[^/]{300,}$", url):
            return False

        return ".ics.uci.edu" in parsed.hostname \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        return False
