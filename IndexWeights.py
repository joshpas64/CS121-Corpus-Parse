import math
from nltk.tokenize import MWETokenizer, wordpunct_tokenize
from nltk.corpus import stopwords
STOPWORDS = set(stopwords.words('english'))
def returnTrimmedList(content):
    contentList = content.split()
    trimmed = [word for word in contentList if word not in STOPWORDS]
    return trimmed
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
    strippedList = [word for word in contentList if word not in STOPWORDS]
    return tuple(strippedList)
def makeSearchToken(phrase):
    contentList = phrase.lower().strip().split()
    wordTrim = [word for word in contentList if word not in STOPWORDS]
    if len(wordTrim) <= 1:
        return phrase
    else:
        return "_".join(wordTrim)

if __name__ == "__main__":
    print("Index Weights as a standalone module")
    query = "donald BREn"
    mweToken = makeIntoMWEToken(query)
    searchToken = makeSearchToken(query)
    file = open("WEBPAGES_CLEAN/0/29","r",encoding="utf-8")
    contentList = file.read().lower().split()
    file.close()
    print(getWordCount(searchToken,mweToken,contentList))
