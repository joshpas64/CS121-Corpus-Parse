import math
def getWordCount(word,fileContentList):
    count = 0
    for i in fileContentList:
        if word.lower() == i.lower():
            count += 1
    return count
def getTfDfScore(count):
    if count == 0:
        return 0
    return (math.log(count,10) + 1)
def getQueryWeight(query,document): ####NOT DONE FIX THIS 
    words = query.split()
    score = 0
    for word in words:
        score += getTfDfScore(getWordCount(word,document)) 
    return score
