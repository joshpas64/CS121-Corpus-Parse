from bs4 import BeautifulSoup
import IndexWeights
import os
import re
import nltk
import json
from pprint import pprint
from lxml import etree, html
from bson import ObjectId
from pymongo import MongoClient
from html.parser import HTMLParser
## The only tags to search for in the html files noted in the canvas document
## Style will be inverted index
KEY_TAGS = ["h1","h2","h3","b","strong"]
TAG_EXP = r'<title>|<h1>|<h2>|<h3>|<b>|<strong>|<p>|</p>|&amp|&lt|&gt'
## The json file gives a key, map of url -> corresponding filepath
EXCLUDED_FILENAMES = ["bookkeeping.json","bookkeeping.tsv"]
## Inverted Index Construction Sort Terms in documents alphabetically
## Key-Value: Term -> List of DocIds in ascending order ([1,4,6,12,20])
## Goal of this program script turn key terms into
## Template insert into a collection
## priority_sum can be a uniquely generated number based off a search terms
## total
## {_id: Objectid(id),query:"Search term",priority:{"title":12,"h1":34,"h2":12,
##      "h3":55,"b":88,"strong":92,priority_sum:523}
HOST = "localhost"
PORT = 27017
client = MongoClient(HOST,PORT)
use_db = client["HW3_Corpus"]
mainCollection = use_db["HW3_Corpus"]
docs = mainCollection.find({})
sample_obj = mainCollection.find_one({"query":"Mondingo"})
#mainCollection.save(sample_obj)
#pprint.pprint(mainCollection.find_one({"query":"Mondingo"}))
json_file = open("WEBPAGES_CLEAN/bookkeeping.json","r")
json_content = json_file.read()
json_file.close()
json_obj = json.loads(json_content)
JSON_PAIRS = list(json_obj.items())
## The individual files do not contain any information 
print(JSON_PAIRS[0])
print(len(json_obj))
def check_if_clean(tagList):
    count = -1
    for i in tagList:
        count += 1
        if len(i.contents) > 1:
            tagList[count] = i.contents[0]
##if soup.title == None:
##    index = html_test_content.find("<body>")
##    print(index)
##    print(html_test_content[0:index].strip("\n").strip("\t"))
##for i in KEY_TAGS:
##    currentList = soup.find_all(i)
##    for e in currentList:
##        print(e.contents[0].strip("\n").strip("\t"))
##for i in sList:
##    print(i.contents[0])
#mainCollection.insert({"query":"Mondingo","priority":{"h1":3,"h2":4,"h3":1,"strong":9,"a":22,"priority_sum":142},"marked_tags":39,"count":211,"line_numbers":[{"file_name":"WEBPAGES_CLEAN/0/24","lines":[12,13,54]}],"urls":[{"url":"https://fano.ics.uci.edu"}]})
def makeMongoCollection(hostname,port,name,table):
    client = MongoClient(hostname,port)
    database = client[name]
    collection = database[table]
    return collection
def makeDocument(word,dbTable):
    if dbTable.find_one({"query":word}) != None:
        return dbTable.find_one({"query":word})
    else:
        baseDocument = {}
        baseDocument["query"] = word
        baseDocument["priority"] = {"title":0,"h1":0,"h2":0,"h3":0,"strong":0,"b":0}
        baseDocument["tagRank"] = 0
        baseDocument["tagSum"] = 0
        baseDocument["count"] = 0
        baseDocument["document_frequency"] = 0
        baseDocument["file_matches"] = []
        baseDocument["scores"] = []
        baseDocument["rank"] = -1
        dbTable.insert(baseDocument)
        return baseDocument
class DbEntry:
    def __init__(self,dbHost,dbPort,dbName,tableName,searchQuery):
        self.mainCollection = makeMongoCollection(dbHost,dbPort,dbName,tableName)
        self.searchPhrase = searchQuery
        self.queryDocument = makeDocument(self.searchPhrase,self.mainCollection)
    def checkTitle(self,content,soupObj):
        titleString = soupObj.find('title')
        if titleString != None:
            return IndexWeights.getWordCount(self.searchPhrase,titleString.string.split())
        else:
            index = content.find("<body>")
            if index == -1:
                return 0
            else:
                titlePortion = content[:index]
                return IndexWeights.getWordCount(self.searchPhrase,titlePortion.split())
    def updateEntry(self,urlName,urlFile):
        try:    
            baseFile = open(urlFile,"r")
            html_content = baseFile.read()
            soup = BeautifulSoup(html_content,"lxml")
            titleCount = self.checkTitle(html_content,soup)
            if titleCount > 0:
                self.queryDocument["priority"]["title"] += 1
            fileString = str(soup.find("body")).strip("<body>").strip("</body>")##get and return word count of base content first. Then check if it fits any tags
            #fileList = re.split(r'\W|\s',fileString)
            fileLines = re.split(r'\n',fileString)
            doc_count = 0
            doc_lines = []
            currentLine = 1
            for line in fileLines:
                noTags = re.split(TAG_EXP,line)
                newString = "".join(noTags)
                simpleList = re.split(r'\W+',newString)
                base_count = IndexWeights.getWordCount(self.searchPhrase,simpleList)
                if base_count > 0:
                    doc_lines.append(currentLine)
                currentLine += 1
                doc_count += base_count
            self.queryDocument["count"] += doc_count
            totalTags = 0
            for tag in KEY_TAGS:
                tagList = soup.find_all(tag)
                tagCount = 0
                for item in tagList:
                    if IndexWeights.getWordCount(self.searchPhrase,item.string.split()) > 0:
                        tagCount += 1
                        totalTags += 1
                self.queryDocument["priority"][tag] += tagCount
            self.queryDocument["tagSum"] += totalTags
            if doc_count > 0:
                self.queryDocument["document_frequency"] += 1
                fileDict = {}
                fileDict["file_name"] = urlFile
                fileDict["file_url"] = urlName
                fileDict["lines"] = doc_lines
                self.queryDocument["file_matches"].append(fileDict)
                doc_score = {}
                doc_score[urlFile] = IndexWeights.getTfDfScore(doc_count)
                self.queryDocument["scores"].append(doc_score)
        except FileNotFoundError: ##Handle OS and FileErrors
            print("There has been a File I/O error\n.The file or pathname you have selected likely does not exist.\nPlease try another filename")
        except PermissionError:
            print("You do not have permission to read this file.\n Try another file or go into you OS and change the file permissions")
        except UnicodeDecodeError:
            print("There are characters or data in this file that does not match the ASCII or UTF-8 characters this program handles.")
            baseFile.close()
        else:
            baseFile.close()
def modifyObject(query,path):
    pass
def makeObject(query,path):
    document = {}
    return document
def runQuery(query,fileName,dbCollection):
    if dbCollection.find_one({}) == None:
        makeObject(query,path,dbCollection)
start = DbEntry(HOST,PORT,"HW3_Corpus","HW3_Corpus","Triangulation")
print(start.queryDocument)
start_pair = JSON_PAIRS[1]
start.updateEntry("www.ics.uci.edu/~dock/manuals/cgal_manual/Triangulation_2_ref/Enum_Triangulation_2-Traits-Tds---Locate_type.html","WEBPAGES_CLEAN/34/311")
print(start.queryDocument)
#####    Sample Output on my Python3.5 Shell #########
## ('12/187', 'www.ics.uci.edu/~wmt/ecoRaft') An example of file-url pairing from the bookkeeping.json file
## 37497 Number of file-url pairings
## {'tagRank': 0, 'count': 0, 'document_frequency': 0, '_id': ObjectId('5922611bcf54c717784070aa'), 'tagSum': 0, 'scores': [], 
##  'file_matches': [], 'priority': {'h2': 0, 'h3': 0, 'title': 0, 'b': 0, 'h1': 0, 'strong': 0}, 'rank': -1, 'query': 'Triangulation'} 
##  Object at initialization, search_query: 'Triangulation'
## {'tagRank': 0, 'count': 4, 'document_frequency': 1, '_id': ObjectId('5922611bcf54c717784070aa'), 'tagSum': 0, 
##  'scores': [{'WEBPAGES_CLEAN/34/311': 1.6020599913279623}], 'file_matches': [{'file_name': 'WEBPAGES_CLEAN/34/311', 
##  'file_url': 'www.ics.uci.edu/~dock/manuals/cgal_manual/Triangulation_2_ref/Enum_Triangulation_2-Traits-Tds---Locate_type.html', 
##  'lines': [37, 53, 54, 56]}], 'priority': {'h2': 0, 'h3': 0, 'title': 0, 'b': 0, 'h1': 0, 'strong': 0}, 'rank': -1, 'query': 'Triangulation'}
##   Object after it had searched through a file that had its query in it.

### can use start.mainCollection.save(start.queryDocument) to save and update entry to MongoDB database



