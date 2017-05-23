import math
from nltk.tokenize import MWETokenizer
def getWordCount(word,mweToken,fileContentList):
    count = 0
    tokenizer = MWETokenizer([mweToken])
    tokenList = tokenizer.tokenize(fileContentList)
    for i in tokenList:
        if word.lower() == i.lower():
            count += 1
    return count
def getTfDfScore(count):
    if count == 0:
        return 0
    return (math.log(count + 1,10))
def getQueryWeight(query,document): ####NOT DONE FIX THIS 
    words = query.split()
    score = 0
    for word in words:
        score += getTfDfScore(getWordCount(word,document)) 
    return score
def getIdfScore(docTotal,docFreq):
    if docFreq == 0:
        return 0
    return math.log((float(docTotal)/docFreq),10)
def makeIntoMWEToken(phrase):
    contentList = phrase.lower().strip().split()
    return tuple(contentList)
def makeSearchToken(phrase):
    contentList = phrase.lower().strip().split()
    if len(contentList) <= 1:
        return phrase
    else:
        return "_".join(contentList)
