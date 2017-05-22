# -*- coding: UTF-8 -*-

# jsonpickle is a library that turns complex objects into JSON representations
# at http://jsonpickle.github.io/
# pip install -U jsonpickle
import jsonpickle

# (object) added for jsonpickle decoding
class Info(object):
    def __init__(self, term, fileName, url):
        self.term = term
        self.priority = ""
        self.count = 1
        self.fileName = fileName
        self.url = url


# Send info objects to this function one at a time while parsing	
# Info objects are added to 3 different maps to build index later	
def infoToMap(info):
    index[info.term] = info
    fileNameMap[info.fileName] = info
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
		

# for testing
index = {}
fileNameMap = {}
urlMap = {}
info = Info("hello", "file name", "www.file.com")
infoToMap(info)
#writeToFile()
loadFromFile()

print index["hello"].fileName
