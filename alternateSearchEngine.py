# -*- coding: UTF-8 -*-

# jsonpickle is a library that turns complex objects into JSON representations
# at http://jsonpickle.github.io/
# pip install -U jsonpickle
import jsonpickle
import CorpusParser
# (object) added for jsonpickle decoding
class Info(object):
    def __init__(self, term, fileName, url):
        self.term = term
        self.priority = ""
        self.count = 1
        self.fileName = fileName
        self.url = url
## Make smaller sized info object from only the needed fields of the
## document object retrieved from parsing or fetched from the database
def createFrom(document):
    searchTerm = document["query"]
    ##scores = document["scores"] ##Extra field to add for ranking later
    ##doc_freq = document["document_frequency"] ##Once again something to consider for scoring later
    fileNames = []
    urlNames = []
    for fileObject in document["file_matches"]:
        fileNames.append(fileObject["file_name"])
        urlNames.append(fileObject["file_url"])
    newInfo = Info(searchTerm,fileNames,urlNames)
    newInfo.count = document["count"]
    newInfo.priority = document["priority"]
    return newInfo
# Send info objects to this function one at a time while parsing	
# Info objects are added to 3 different maps to build index later

##class URL(object):
##    def __init__(self, name, score, fileName):
##        self.name = name
##        self.count = 1
##        self.score = score
##        self.file = fileName
##
##def infoToMap(info):
##    urlObject = URL(info.url, 0, info.file)
##    # Check if term exists and proceed accordingly
##    if info.term in index:
##        # Term exists in dictionary, update URL list
##        if urlObject.name in index[info.term].links:
##            index[info.term].links[urlObject.name].count += 1
##
##            # TODO
##            # .score will be some equation that builds a score from what we have
##            # it will score differently for h1, h2, bold, etc...
##            # this is a placeholder
##            index[info.term].links[urlObject.name].score += 1
##        else:
##            index[info.term].links[urlObject.name] = urlObject
##    else:
##        # Create new entry for new term
##        info.links[urlObject.name] = urlObject
##        index[info.term] = info
##    # temporary maps that may be useful later
##    fileNameMap[info.file] = info
##    urlMap[info.url] = info
def infoToMap(info):
    index[info.term] = info
##    fileNameMap[info.fileNames] = info
##    urlMap[info.url] = info
    fileNameMap["fileNames"] = info ## This was to prevent Type Error since these fields are now lists 
    urlMap["urls"] = info ## which are unhashable by python's standard library implementation

# Run writeToFile() when parsing is complete to write to file	
def writeToFile():
    indexPickle = jsonpickle.encode(index)
    filePickle = jsonpickle.encode(fileNameMap)
    urlPickle = jsonpickle.encode(urlMap)
    with open('indexJSON.txt', 'w') as indexFile:  
        indexFile.write(indexPickle)
    with open('fileNameJSON.txt', 'w') as fileNameFile: 
        fileNameFile.write(indexPickle)
    with open('urlMapJSON.txt', 'w') as urlMapFile:
        urlMapFile.write(indexPickle)

# Run loadFromFile if running the program after the files have been made
def loadFromFile():
    with open('indexJSON.txt', 'r') as indexFile:  
        temp = indexFile.read()
        index = jsonpickle.decode(temp)
    with open('fileNameJSON.txt', 'r') as fileNameFile: 
        temp = fileNameFile.read()
        fileNameMap = jsonpickle.decode(temp)
    with open('urlMapJSON.txt', 'r') as urlMapFile:
        temp = urlMapFile.read()
        urlMap = jsonpickle.decode(temp)     
		

# for testing
index = {}
fileNameMap = {}
urlMap = {}
##info = Info("hello", "file name", "www.file.com")
##infoToMap(info)
##writeToFile()
##loadFromFile()
##print(index["hello"].fileName)
if __name__ == "__main__":
    myMainCollection = CorpusParser.makeMongoCollection(CorpusParser.HOST,CorpusParser.PORT,"HW3_Corpus","HW3_Corpus")
    irvineDoc = myMainCollection.find_one({"query":"irvine"})
    irvineInfo = createFrom(irvineDoc)
    infoToMap(irvineInfo)
    writeToFile()
    loadFromFile()
    print(index["irvine"].fileName)
