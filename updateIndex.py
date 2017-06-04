#If you want to add a unique word to the index, you can do so by typing this in the Python shell or in a new .py file

#The file should look like this: 

import CorpusParser, queryIndex
from SearchEngine import score

def runQuery(query):
    print("Import successful")
    ## This will take a query and search through ALL 37,497 files in the WEBPAGES_CLEAN Corpus Folder
    corpus = CorpusParser.getCorpusReference("WEBPAGES_CLEAN/bookkeeping.tsv") ### Retrieve all file-name, url-pairs
    entry = CorpusParser.incrementalQuery(query,corpus,0,CorpusParser.DOCUMENT_TOTAL) ## An actual query through the whole corpus looks like this
    print("Finished Parsing")   ## For debugging purposes you can iterate over the corpuse file by file or by number of files by adjusting its
    print("Updating Database")   ## Start and Stop Index
    entry.saveToDb()     ### Save any new entries to the MongoDB database table
    print("Done with run-through")
    indexToUpdate = queryIndex.preloadIndex() ## Update the index object and write it to the index files
    indexToUpdate = score(indexToUpdate) ## Implement the scoring technique on the object
    return indexToUpdate
runQuery("ENTER YOUR QUERY HERE") ## You can put either one-word or multiword queries Corpus Parser handles multi-word queries and stopwords automatically     
        
    
    
