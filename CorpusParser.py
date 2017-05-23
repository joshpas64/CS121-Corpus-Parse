from bs4 import BeautifulSoup
import IndexWeights
import os
import re
from pprint import pprint ##For debugging
from lxml import etree, html
from bson import ObjectId
from pymongo import MongoClient
from html.parser import HTMLParser

###BONUS POINT
## Remove stop words in tokenizing steps use NLTK
## Using stemming or collapsing similar words into one word
##  for similar word queries
## Add GUI window


##NLTK Library check
##how to get out of codec errors
##use open("filename","r",encoding="ASCII" or encoding="UTF-8")
##

## The only tags to search for in the html files noted in the canvas document
## Style will be inverted index
KEY_TAGS = ["h1","h2","h3","b","strong"]
TAG_EXP = r'<title>|<h1>|<h2>|<h3>|<b>|<strong>|<p>|</p>|&amp|&lt|&gt'
## The json file gives a key, map of url -> corresponding filepath
EXCLUDED_FILENAMES = ["bookkeeping.json","bookkeeping.tsv"]
DOCUMENT_TOTAL = 37497
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
DOC_TOTAL = 37497
tsv_file = open("WEBPAGES_CLEAN/bookkeeping.tsv","r",encoding="utf-8")
tsv_content = tsv_file.readlines()
tsv_file.close()
TSV_PAIRS = []
for line in tsv_content:
    pair = line.split()
    TSV_PAIRS.append(pair)
#mainCollection.save(sample_obj)
#pprint.pprint(mainCollection.find_one({"query":"Mondingo"}))
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
def cleanUpTags(tag_exp,line):
    tagFree = re.split(tag_exp,line)
    tagLessString = "".join(tagFree)
    parsed_list = re.split(r'\W+',tagLessString)
    return parsed_list
class DbEntry:
    def __init__(self,dbHost,dbPort,dbName,tableName,searchQuery):
        self.mainCollection = makeMongoCollection(dbHost,dbPort,dbName,tableName)
        self.searchPhrase = searchQuery.lower().strip()
        self.searchToken = IndexWeights.makeSearchToken(self.searchPhrase)
        self.mweToken = IndexWeights.makeIntoMWEToken(self.searchPhrase)
        self.queryDocument = makeDocument(self.searchToken,self.mainCollection)
    def checkTitle(self,content,soupObj):
        titleString = soupObj.find('title')
        if titleString != None:
            if titleString.string == None:
                return 0
            return IndexWeights.getWordCount(self.searchToken,self.mweToken,titleString.string.split())
        else:
            index = content.find("<body>")
            if index == -1:
                return 0
            else:
                titlePortion = content[:index]
                return IndexWeights.getWordCount(self.searchToken,self.mweToken,titlePortion.split())
    def updateEntry(self,urlName,urlFile):
        try:    
            baseFile = open(urlFile,"r",encoding="utf-8")
            html_content = baseFile.read().lower()
            soup = BeautifulSoup(html_content,"lxml")
            titleCount = self.checkTitle(html_content,soup)
            if titleCount > 0:
                self.queryDocument["priority"]["title"] += 1
                self.queryDocument["tagSum"] += 1
            fileString = str(soup.find("body")).strip("<body>").strip("</body>")##get and return word count of base content first. Then check if it fits any tags
            #fileList = re.split(r'\W|\s',fileString)
            fileLines = re.split(r'\n',fileString)
            doc_count = 0
            doc_lines = []
            currentLine = 1
            for line in fileLines:
                simpleList = cleanUpTags(TAG_EXP,line)
                base_count = IndexWeights.getWordCount(self.searchToken,self.mweToken,simpleList)
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
                    if item.string != None and IndexWeights.getWordCount(self.searchToken,self.mweToken,item.string.split()) > 0:
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
    def saveToDb(self):
        self.mainCollection.save(self.queryDocument)
def incrementalQuery(query,corpus,startIndex,stopIndex):
    if startIndex < 0:
        startIndex = 0
    if stopIndex > 37497:
        stopIndex = 37497
    entry = DbEntry(HOST,PORT,"HW3_Corpus","HW3_Corpus",query)
    prefix = "WEBPAGES_CLEAN/"
    for row in range(startIndex,stopIndex):
        entry.updateEntry(corpus[row][1],prefix + corpus[row][0])
    return entry
### A full run through of the WHOLE Corpus would essentially be 
### incrementalQuery("search_term",TSV_PAIRS,0,DOC_TOTAL)
###runQuery("Technical Interviews",TSV_PAIRS)    

#print(start_pair)
#start.updateEntry("www.ics.uci.edu/~dock/manuals/cgal_manual/Triangulation_2_ref/Enum_Triangulation_2-Traits-Tds---Locate_type.html","WEBPAGES_CLEAN/34/311")
#start.mainCollection.save(start.queryDocument)
##start2 = DbEntry(HOST,PORT,"HW3_Corpus","HW3_Corpus","Technical Interviews")
##start2.updateEntry("wics.ics.uci.edu/author/leejacqueline?afg64_page_id=3&afg66_page_id=2&afg60_page_id=2&afg58_page_id=4&afg65_page_id=4","WEBPAGES_CLEAN/0/51")
##print(start2.queryDocument)
##start2.saveToDb()

if __name__ == "__main__":
    client = MongoClient(HOST,PORT)
    use_db = client["HW3_Corpus"]
    mainCollection = use_db["HW3_Corpus"]
    docs = mainCollection.find({})
    sample_obj = mainCollection.find_one({"query":"Mondingo"})
    print(len(TSV_PAIRS))
    ## The individual files do not contain any information 
    print(TSV_PAIRS[0])
    start = DbEntry(HOST,PORT,"HW3_Corpus","HW3_Corpus","Triangulation")
    print(start.queryDocument)
    print("\n\n")
    irvineEntry = incrementalQuery("Irvine",TSV_PAIRS,30000,37497) ## Was testing and updating incrementally to check for bugs
    print("DONE PROCESSING")
    irvineEntry.saveToDb()
