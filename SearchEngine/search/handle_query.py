import json
import os
import heapq
import math
import re
from django.conf import settings
from nltk import PorterStemmer
from pymongo import MongoClient
from bs4 import BeautifulSoup

db = MongoClient().searchdb
ps = PorterStemmer()

def CosineScore(terms):
    N = db.index.find_one({"_size": {"$exists": True}})['_size']

    # index is a dictionary containing the term: postings pairs
    index = {}
    # all_doc contains all the docid that this query could return
    all_doc = set()
    for term in terms:
        cursor = db.index.find_one({"term": term})
        if cursor:
            index[term] = cursor['postings']
            all_doc.update(cursor['postings'].keys())
    # index_by_idf is a dictionary of term with decreasing idf
    term_by_idf = sorted(index.items(), key=lambda x: len(x[1]))
    # the doc should at least contains 3/4 of the query terms
    doc_filter = int(len(term_by_idf) * 3 / 4)

    # find the doc that contains at least 3/4 of the query terms using set intersection
    for i in range(0, doc_filter):
        all_doc.intersection_update(term_by_idf[i][1].keys())

    # doc_score is in {doc1: {term1: tfidf1, term2: tfidf2...}, ...} format
    doc_score = {}
    for doc in list(all_doc):
        doc_score[doc] = {}
        for term in index.keys():
            if doc in index[term]:
                doc_score[doc][term] = index[term][doc]
            else:
                doc_score[doc][term] = 0

    # score contains the normalized score of each doc, in {docid: score, ...} format
    score = {}
    for doc in doc_score:
        doc_length = 0
        for weight in doc_score[doc].values():
            doc_length += weight * weight
        doc_length = math.sqrt(doc_length)
        each_score = 0
        for term in doc_score[doc]:
            each_score += doc_score[doc][term]
        score[doc] = each_score / doc_length
    # use heap sort instead of sorted to increase efficiency
    return [k for (k, v) in heapq.nlargest(10, score.items(), key=lambda x: x[1])]


def handle_query(query):
    file_path = os.path.join(settings.STATIC_ROOT, 'WEBPAGES_RAW/bookkeeping.json')
    with open(file_path) as json_data:
        bookkeeping = json.load(json_data)

    raw_query = query.split()
    query = set()
    for term in raw_query:
        query.add(ps.stem(term))
    query = list(query)

    # if there is only one term in query, get the results url by sorting on tfidf of this term's posting list
    if len(query) == 1:
        cursor = db.index.find_one({"term": query[0]})
        result = []
        if cursor:
            result = [k for (k, v) in heapq.nlargest(10, cursor['postings'].items(), key=lambda x: x[1])]
    # if there are more than one query term, call ConsineScore function, which return list of docids
    else:
        result = CosineScore(query)

    # final_result is a dictionary in the format of {url:snippet}
    final_result = {}
    for doc in result:
        file_name = 'WEBPAGES_RAW/' + doc
        file_name = os.path.join(settings.STATIC_ROOT, file_name)
        with open(file_name, 'r') as content:
            soup = BeautifulSoup(content, "html.parser")
            # split the plain text of each files
            lines = re.split(r"\.|\s{2,}|\n", soup.get_text())
            snippet = ''
            for line in lines:
                # if the line is too long, ignore it
                if len(re.findall(r"[\w']+", line)) >= 100:
                    continue
                # check if any query term in this line
                if any((' '+term) in line.lower() for term in query):
                    # keep the length of snippet lower than 100 words
                    if len(re.findall(r"[\w']+", snippet)) >= 100:
                        break
                    snippet += line + '...'
            final_result[bookkeeping[doc]] = snippet
    return final_result
