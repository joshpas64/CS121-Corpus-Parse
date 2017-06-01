import SearchEngine
import CorpusParser
import json

## If a database is updated with new terms the index can be preloaded with
## the parseFromDoc function without having to reiterate through the whole
## corpus
def parseFromDoc(document):
    currentQuery = document["query"]
    infoList = []
    doc_freq = document["document_frequency"]
    for fileObj in document["file_matches"]:
        currentUrl = fileObj["file_url"]
        currentFile = fileObj["file_name"]
        tags = fileObj["tags_encountered"]
        currentScore = fileObj["tfScore"]
        currentLines = fileObj["lines"]
        newInfo = SearchEngine.Info(currentQuery,currentUrl,currentScore,currentFile)
        newInfo.priority = tags
        infoList.append(newInfo)
        SearchEngine.infoToMap(newInfo)
if __name__ == "__main__":
    print("Ran as the main file")
    indexDict,fileDict,urlDict = SearchEngine.loadFromFile()
    referenceCollection = CorpusParser.makeMongoCollection(CorpusParser.HOST,CorpusParser.PORT,"HW3_Corpus","HW3_Corpus")
    collections = referenceCollection.find()
    for col in collections:
        parseFromDoc(col)
    SearchEngine.writeToFile()
## Sample run through on individual records
##    doc = referenceCollection.find_one({"query":"wics"})
##    parseFromDoc(doc)
##    doc2 = referenceCollection.find_one({"query":"machine_learning"})
##    parseFromDoc(doc2)
##    SearchEngine.writeToFile()
##    print(len(indexDict["machine_learning"].links))
##    print(indexDict["machine_learning"].queue)
##    print("learning" in indexDict)
##    count = 0
##    for key in indexDict["machine_learning"].links:
##        if count >= 10:
##            break
##        print(indexDict["machine_learning"].links[key].name)
##        print(indexDict["machine_learning"].links[key].count)
##        count += 1
    index = SearchEngine.loadFromFile()[0]
    print("machine_learning" in index)
    print("wics" in index)
    print("informatics" in index)
    print("Done with links")
    
