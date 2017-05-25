from bs4 import BeautifulSoup
import IndexWeights
import os
import re
from pprint import pprint ##For debugging
from lxml import etree, html
from bson import ObjectId
from pymongo import MongoClient
import SearchEngine
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
#### Tags and HTML notation that is checked when the documents are being parsed 
TAG_EXP = r'<title>|<h1>|<h2>|<h3>|<b>|<strong>|<p>|</p>|&amp|&lt|&gt'

## The json file gives a key, map of url -> corresponding filepath
EXCLUDED_FILENAMES = ["bookkeeping.json","bookkeeping.tsv"]
DOCUMENT_TOTAL = 37497 ## Number of documents in the whole Corpus Folder
### On Canvas, some files namely, the ones that contain the word 'dataset' url have been found to be junk files
### As well as some files containing just numbers or NON-ASCII characters so perhap adding functionality to see
### and skip over these files could be useful


## Inverted Index Construction Sort Terms in documents alphabetically
## Key-Value: Term -> List of DocIds in ascending order ([1,4,6,12,20])
## Goal of this program script turn key terms into
## Template insert into a collection
## priority_sum can be a uniquely generated number based off a search terms
## total
## {_id: Objectid(id),query:"Search term",priority:{"title":12,"h1":34,"h2":12,
##      "h3":55,"b":88,"strong":92,priority_sum:523}

## If you have MongoDB on your local computer just use these as HOST and PORT parameters for establishing connection
HOST = "localhost"
PORT = 27017


def getCorpusReference(tsv_fileName):
    tsv_pairs = []  ## Lines containing the pairs of URL's and Filename's associated with them
    try:
        tsv_file = open(tsv_fileName,"r",encoding="utf-8") 
        content = tsv_file.readlines() ## List of lines that contain the url, filename pairs in .tsv file
        for line in content:
            pair = line.split() ## Make a list of length 2 containing the fileName followed by the URL
            tsv_pairs.append(pair) ## Add it to the list of pairs
        return tsv_pairs
    except FileNotFoundError: ##Handle OS and FileErrors
        print("There has been a File I/O error\n.The file or pathname you have selected likely does not exist.\nPlease try another filename")
    except PermissionError:
        print("You do not have permission to read this file.\n Try another file or go into you OS and change the file permissions")
    except UnicodeDecodeError:
        print("There are characters or data in this file that does not match the ASCII or UTF-8 characters this program handles.")
        tsv_file.close()
    else:
        tsv_file.close()
def makeMongoCollection(hostname,port,name,table):
    client = MongoClient(hostname,port) ## Create a MongoDB client-side connection with specified hostname and port numbers
    database = client[name] ## Retrieve specified database
    collection = database[table]
    return collection ## Retrieve and return specified table or collection of objects in the database
def makeDocument(word,dbTable):
    if dbTable.find_one({"query":word}) != None:
        return dbTable.find_one({"query":word}) ## Return the already existing document object so it can be updated
    else:
        baseDocument = {} ## If the term does not exist make object that follows the template below
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
        self.mainCollection = makeMongoCollection(dbHost,dbPort,dbName,tableName)  ## Retrieve or make a Document Template from the database
        self.searchPhrase = searchQuery.lower().strip() 
        self.searchToken = IndexWeights.makeSearchToken(self.searchPhrase) ## Normalized search token, converts to lower-case strips out whitespace and makes into MWE token
                                                                            ## if token is more than 1 word
        self.mweToken = IndexWeights.makeIntoMWEToken(self.searchPhrase) ## Turn search token into MWE_TOKEN for use in the tokenizing portion of the program
        self.queryDocument = makeDocument(self.searchToken,self.mainCollection)
    def checkTitle(self,content,soupObj):
        titleString = soupObj.find('title') ## To handle cases when there is text before the <body> but no <title></title> tags
        if titleString != None: ## If there are title tags
            if titleString.string == None: ##If there is no content in between title tags
                return 0
            return IndexWeights.getWordCount(self.searchToken,self.mweToken,titleString.string.split()) ##Check if search term is between <title></title>
        else:
            index = content.find("<body>") ##If no tag's find index in fileString where the body occurs
            if index == -1: ##In case there are no body tags either
                return 0
            else:
                titlePortion = content[:index] ##Get portion before the <body> tag
                return IndexWeights.getWordCount(self.searchToken,self.mweToken,titlePortion.split()) ##That content will count as title and check if there are any matches there
    def updateEntry(self,urlName,urlFile):
        try:    
            baseFile = open(urlFile,"r",encoding="utf-8") ##Open the file use 'utf-8' encoding to prevent CodecErrors 
            html_content = baseFile.read().lower() ##Turn all content to string and lowerCase it
            soup = BeautifulSoup(html_content,"lxml") ##Make HTML parsing object with BeautifulSoup
            tagObject = {"title":0,"h1":0,"h2":0,"h3":0,"strong":0,"b":0} ## Default "tag_reference" object for each file if there are any HTML tag matches
            titleCount = self.checkTitle(html_content,soup) ##Check if the search Term is in the title portion
            if titleCount > 0:
                self.queryDocument["priority"]["title"] += 1  ##Increment objects accordingly if the term has a match in the title 
                self.queryDocument["tagSum"] += 1
                tagObject["title"] += 1
            fileString = str(soup.find("body")).strip("<body>").strip("</body>")##get and return word count of base content first. Then check if it fits any tags
            fileLines = re.split(r'\n',fileString) ## To check line by line and add to file's line_count object if there are any hits
            doc_count = 0 ##Amount of times the term has a match
            doc_lines = [] ##List of lines in the file to which the term made a match
            currentLine = 1 ## Starting Line
            for line in fileLines:
                simpleList = cleanUpTags(TAG_EXP,line) ##Parse out any broken or unnecessary HTML tags or markup i.e (<p>, &amp, &lt)
                base_count = IndexWeights.getWordCount(self.searchToken,self.mweToken,simpleList) ## Get word count matches for line
                if base_count > 0:
                    doc_lines.append(currentLine) ##Add to list of matching lines if there is a match
                currentLine += 1 
                doc_count += base_count ##Add to total term match count for the whole file
            self.queryDocument["count"] += doc_count ## Add to the term's document Object (database record) the amount of times the term matched
            totalTags = 0 ## Number of all tag encounters 
            ## Check the if there are HTML tag matches [<h1>,<h2>,<h3>,<b>,<strong>]
            for tag in KEY_TAGS:
                tagList = soup.find_all(tag) ##Get list of all tag's that match that tag i.e get all 'h1' tags
                tagCount = 0 ## Have a counter for each type of tag
                for item in tagList:
                    if item.string != None and IndexWeights.getWordCount(self.searchToken,self.mweToken,item.string.split()) > 0:
                        tagCount += 1 ##If there are matches add to tagCount and totalTags
                        totalTags += 1
                self.queryDocument["priority"][tag] += tagCount ##Update the record's HTML tagObject which keeps record of tag matches for the term itself
                tagObject[tag] += tagCount ## Update tagObject that contains matches to tag for this file only
            self.queryDocument["tagSum"] += totalTags
            if doc_count > 0:
                self.queryDocument["document_frequency"] += 1 ##In the case of match, update dF count for the term
                fileDict = {} ##Base file object to add to the term document
                fileDict["file_name"] = urlFile ##Add file's name
                fileDict["file_url"] = urlName ## Add file's URL
                fileDict["tags_encountered"] = tagObject ## Add the HTML tag matches for the file for the search term
                fileDict["lines"] = doc_lines ## Add which lines it matched  to
                doc_score = {}
                file_score = IndexWeights.getTfDfScore(doc_count) ## Get the TfDf score for the term and document, idf is gathered once query has finished the whole collection
                doc_score[urlFile] = file_score ## Add score to document_object 
                fileDict["tfScore"] = file_score ## Add score to file_object 'tfScore' field
                self.queryDocument["file_matches"].append(fileDict)  ## Add it to the list of files that matches
                self.queryDocument["scores"].append(doc_score)
                newInfo = SearchEngine.Info(self.searchToken,urlName,file_score,urlFile) ## Make an info from the search term and file's url,score,and name
                SearchEngine.infoToMap(newInfo) ## Update index objects in SearchEngine.py
                SearchEngine.writeToFile() ## Update index Files
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
        self.mainCollection.save(self.queryDocument) ## Save the query record and its information back to the MongoDB Database

###Incrementing through the Corpus File by File for debugging purposes
### Start Index and StopIndex are line positions in the bookkeeping.tsv file
def incrementalQuery(query,corpus,startIndex,stopIndex):
    if startIndex < 0:   ## Index Checks
        startIndex = 0
    if stopIndex > 37497:
        stopIndex = 37497
    entry = DbEntry(HOST,PORT,"HW3_Corpus","HW3_Corpus",query) ## Make a DbEntry to update the document the query it refers to in the Database as well as the index
    prefix = "WEBPAGES_CLEAN/"          ### Corpus folder prefix
    for row in range(startIndex,stopIndex):
        entry.updateEntry(corpus[row][1],prefix + corpus[row][0])
    return entry ##Return entry object if one wants to get the document object it retrieve its fields or save any changes its found back to the database it refers to

if __name__ == "__main__":
    print("Import successful")
    corpus = getCorpusReference("WEBPAGES_CLEAN/bookkeeping.tsv") ###Example Run-Through with key term 'machine learning'
    entry = incrementalQuery("machine  learNing",corpus,0,10000) ## An actual query through the whole corpus looks like this
    print("Finished Parsing")   ## For debugging purposes you can iterate over the corpuse file by file or by number of files by adjusting its
    print("Updating Database")   ## Start and Stop Index
    entry.saveToDb()     ### Save any new entries to the MongoDB database table
    print("Done with run-through")
