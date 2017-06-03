import math
from nltk.tokenize import MWETokenizer
from nltk.corpus import stopwords
STOPWORDS = set(stopwords.words("english"))

def getWordCount(word,mweToken,fileContentList):
    count = 0
    trimmed = [words for words in fileContentList if words not in STOPWORDS]
    tokenizer = MWETokenizer([mweToken])
    tokenList = tokenizer.tokenize(trimmed)
    for i in tokenList:
        if word.lower() == i.lower():
            count += 1
    return count
def getTfDfScore(count):
    if count == 0:
        return 0
    return (math.log(count + 1,10))
def getIdfScore(docTotal,docFreq):
    if docFreq == 0:
        return 0
    return math.log((float(docTotal)/docFreq),10)
def makeIntoMWEToken(phrase):
    contentList = phrase.lower().strip().split()
    strippedContentList = [words for words in contentList if words not in STOPWORDS]
    return tuple(strippedContentList)
def makeSearchToken(phrase):
    contentList = phrase.lower().strip().split()
    if len(contentList) <= 1:
        return phrase
    else:
        return "_".join(contentList)
