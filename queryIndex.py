import SearchEngine
import CorpusParser
import IndexWeights
import json

## If a database is updated with new terms the index can be preloaded with
## the parseFromDoc function without having to reiterate through the whole
## corpus
HTML_WEIGHTS = {"title":25,"h1":10,"h2":7.5,"h3":5,"b":2,"strong":2}
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
        newInfo = SearchEngine.Info(currentQuery,currentUrl,currentScore,currentFile,tags)
        infoList.append(newInfo)
        SearchEngine.infoToMap(newInfo)
def score(infoObject,length):
    """
    This to generate the final score to be used for ranking
    """
    tfidfScore = IndexWeight.getIdfScore(infoObject.score,length)
    htmlScore = 0
    for key in infoObject.priority:
        count = infoObject.priority[key]
        htmlScore += (HTML_WEIGHTS[key] * count)
    return infoObject.score + htmlScore
def preloadIndex():
    indexDict,fileDict,urlDict = SearchEngine.loadFromFile()
    referenceCollection = CorpusParser.makeMongoCollection(CorpusParser.HOST,CorpusParser.PORT,"HW3_Corpus","HW3_Corpus")
    collections = referenceCollection.find({})
    for col in collections:
        parseFromDoc(col)
    SearchEngine.writeToFile()
    index = SearchEngine.loadFromFile()[0]
    return index
def getIndexKey(term,index):
    length = len(index[term].links)
    sortedList = sorted(index[term].links.items(),key=lambda x: score(x[1],length),reverse=True)
    finalList = sortedList[:10]
    for info in finalList:
        print(info[1].score)
    print("Done with links")
if __name__ == "__main__":
    print("Ran as the main file")
    #newIndex = preloadIndex() If database has been updated and the index file needs to be updated
    newIndex = SearchEngine.loadFromFile()[0] ## If database is updated and can be preloaded automatically, this takes less time than preloadIndex()
    newIndex = SearchEngine.score(newIndex)
    print(SearchEngine.search("irvine",newIndex)) ## Get list of results (Items in list are Doc Objects from SearchEngine.py)
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
    
