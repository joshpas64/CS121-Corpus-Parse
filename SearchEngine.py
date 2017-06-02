# -*- coding: UTF-8 -*-

# jsonpickle is a library that turns complex objects into JSON representations
# at http://jsonpickle.github.io/
# pip install -U jsonpickle
import jsonpickle
import queue
global index, fileNameMap, urlMap
# For testing
index = {}
fileNameMap = {}
urlMap = {}
# (object) added for jsonpickle decoding
class Info(object):
    def __init__(self, term, url, score, file,priority):
        self.term = term
        self.priority = priority
        self.score = score
        self.url = url   # only used for building URL object
        self.file = file # only used for building URL object
        self.links = {}  # only used once term is in index dictionary
        self.queue = queue.PriorityQueue()  # TODO This should be a priority queue that sorts Doc objects by score

# Doc classes are only used within Info.links dictionary
# each class has a score associated with it that is updated over time
# as new terms are found.  We have to figure out the scoring part later.
class Doc(object):
    def __init__(self, name, score, fileName):
        self.name = name
        self.count = 1
        self.score = score
        self.file = fileName
    def __eq__(self,other):
        return self.score == other.score
    def __ne__(self,other):
        return self.score != other.score
    def __gt__(self,other): ## To have the priority queue sort in reverse order (descending, highest term first)
        return self.score < other.score
    def __lt__(self,other):
        return self.score > other.score       

# Send info objects to this function one at a time while parsing
# Info objects are added to 3 different maps to build index later
def infoToMap(info):
    docObject = Doc(info.url, info.score, info.file)
    # Check if term exists and proceed accordingly
    if info.term in index:
        # Term exists in dictionary, update File list
        if docObject.name in index[info.term].links:
            index[info.term].links[docObject.name].count += 1
        else:
            index[info.term].links[docObject.name] = docObject
    else:
        # Create new entry for new term
        info.links[docObject.name] = docObject
        index[info.term] = info
    # temporary maps that may be useful later
    fileNameMap[info.file] = info
    urlMap[info.url] = info

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
    return index,fileNameMap, urlMap

# this is where the scoring is done
# This function below will retrieve a final score based on the tfIdf Score of the document and the amount and types of HTML Tags it was in
def scoreDoc(tfScore,docCount,tagObject):
    tfIdf = IndexWeights.getIdfScore(tfScore,docCount)
    htmlScore = 0
    for tag in tagObject:
        tagCount = tagObject[tag]
        tagWeight = HTML_WEIGHTS[tag] * tagCount
        htmlScore += tagWeight
    finalScore = tfIdf + htmlScore
    return finalScore
# This is where a whole index is scored AND SORTED
def score() :
    ''' This is how the scoring can be done:
        N = number of documents containing the term 
        Doc object.count = number of times terms appears in document
        Use the formula from the slides
        After the document is scored, it is added to the info.queue for its term
        
        In search(term) function we can later account for the docObject.priority as well
        
        pseudocode:
        temp = priority queue for doc objects
            for key in index
                for Doc object in index[key.links]
                    score doc object with key.links.size and doc.count
                    temp.add(doc)
                index[key].queue = temp    
                    
                    
        If there is a "concurrent modification error for index[key].queue = temp
            instead create docMap
            then instead of 'index[key].queue = temp' use 'docMap[key] = temp
            afterwards, do
                for key in docMap:
                    index[key].queue = docMap[key].queue
                   '''
##    Possible implementation of scoring the whole index
##    for term in index:
##        temp = queue.PriorityQueue()
##        docCount = len(index[term].links)
##        for key in index[term].links:
##            doc = index[term].links[key]
##            doc.score = scoreDoc(doc.score,docCount,doc.tagCounts)
##            temp.add(doc)
##        index[key].queue = temp
def search(term):
    ''' Here we will return the sorted index[term].queue while accounting for docObjecct.priority as well'''
    if term in index:
        print(term, "found")
    else:
        print(term, "not found")



##info = Info("hello", "www.url.com", 0, "file name here")
##infoToMap(info)
##writeToFile()
##info2 = Info("searching", "www.ics.com", 0, "WEBPAGES_CLEAN/2/1")
##infoToMap(info2)
##writeToFile()
##loadFromFile()

##print(index["hello"].file)
##print(index["hello"].links[info.url].count)
