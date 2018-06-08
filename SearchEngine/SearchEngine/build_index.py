import re
import json
import math
from bs4 import BeautifulSoup
from pymongo import MongoClient
from nltk.stem import PorterStemmer

db = MongoClient().searchdb
ps = PorterStemmer()
with open("WEBPAGES_RAW/bookkeeping.json") as json_data:
    bookkeeping = json.load(json_data)

temp = {}
doc_size = 0
for docId in bookkeeping:
    filename = "WEBPAGES_RAW/" + docId
    if ("BadContent?" in bookkeeping[docId]) or ("ironwood.ics.uci.edu" in bookkeeping[docId]):
        continue
    with open(filename, 'r') as content:
        doc_size += 1
        soup = BeautifulSoup(content, "html.parser")
        plain_text = re.findall(r"[a-zA-Z0-9]+", soup.get_text())
        for word in plain_text:
            word = ps.stem(word).lower()
            if len(word) >= 25:
                continue
            if word in temp:
                if docId in temp[word]:
                    temp[word][docId] += 1
                else:
                    temp[word][docId] = 1
            else:
                temp[word] = {docId: 1}

        title = soup.title
        if title and title.string:
            title = title.string
            title_token = re.findall(r"[a-zA-Z0-9]+", title)
            for word in title_token:
                word = ps.stem(word).lower()
                if word in temp:
                    if docId in temp[word]:
                        temp[word][docId] += 2

        header = soup.h1
        if header and header.string:
            header = header.string
            header_token = re.findall(r"[a-zA-Z0-9]+", header)
            for word in header_token:
                word = ps.stem(word).lower()
                if word in temp:
                    if docId in temp[word]:
                        temp[word][docId] += 1

size_term = {'_size': doc_size}

bash_insert = [size_term]
count = 1
for term in temp:
    if count > 2000:
        add_to_db = db.index.insert_many(bash_insert)
        count = 0
        bash_insert = []
    idf = math.log10(doc_size/float(len(temp[term])))
    for doc in temp[term]:
        temp[term][doc] = (1 + math.log10(temp[term][doc])) * idf
    bash_insert.append({"term": term, "postings": temp[term]})
    count += 1

if bash_insert:
    add_too_db = db.index.insert_many(bash_insert)
