# -*- coding: UTF-8 -*-

# jsonpickle is a library that turns complex objects into JSON representations
# at http://jsonpickle.github.io/
# pip install -U jsonpickle
import jsonpickle

# (object) added for jsonpickle decoding
class Info(object):
    def __init__(self, term, url, score, file):
        self.term = term
        self.priority = ""
        self.score = score
        self.url = url   # only used for building URL object
        self.file = file # only used for building URL object
        self.links = {}  # only used once term is in index dictionary

# URL classes are only used within Info.links dictionary
# each class has a score associated with it that is updated over time
# as new terms are found.  We have to figure out the scoring part later.
class URL(object):
    def __init__(self, name, score, fileName):
        self.name = name
        self.count = 1
        self.score = score
        self.file = fileName

# Send info objects to this function one at a time while parsing
# Info objects are added to 3 different maps to build index later
def infoToMap(info):
    urlObject = URL(info.url, 0, info.file)
    # Check if term exists and proceed accordingly
    if info.term in index:
        # Term exists in dictionary, update URL list
        if urlObject.name in index[info.term].links:
            index[info.term].links[urlObject.name].count += 1

            # TODO
            # .score will be some equation that builds a score from what we have
            # it will score differently for h1, h2, bold, etc...
            # this is a placeholder
            index[info.term].links[urlObject.name].score += 1
        else:
            index[info.term].links[urlObject.name] = urlObject
    else:
        # Create new entry for new term
        info.links[urlObject.name] = urlObject
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

def search(term):
    if term in index:
        print term, "found"
    else:
        print term, "not found"


# For testing
index = {}
fileNameMap = {}
urlMap = {}
info = Info("hello", "www.url.com", 0, "file name here")
infoToMap(info)
writeToFile()
#loadFromFile()

print index["hello"].file
print index["hello"].links[info.url].count