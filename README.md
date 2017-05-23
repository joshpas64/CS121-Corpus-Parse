# CS121-Corpus-Parse
CS 121 Collaborative Project

## Map/Index Logic
The map logic is convoluted so it is listed explicitly here.  By URL I mean doc or link, not necessarily hyperlink.

The parser will create Info objects of type info = Info(term, url, score, file)

They are as follows:<br>
term - string extracted from file<br>
url - url the file came from<br>
file - the name of the file<br>
score - a number relative to how important the term is.    This is something we have to decide, such as 100 for h1, 50 for h2, etc...  It could also be a formula of some kind.

The parser will send Info objects one at a time to infoToMap(info)<br>
Here, the objects are decomposed and placed into appropriate dictionaries as follows:
1. 'index' is the inverted index where search terms are the keys.  Inside are info objects that only use:<br>
a. A 'links' dictionary that holds URL objects<br>
b. URL objects contain: <br>
name = url link<br>
count = # of times this term has appeared in this url<br>
score = who knows we'll figure it out<br>
file name =  where the URL was retrieved<br>
2. urlMap and fileNameMap for optimization later

Searches are performed as follows:
1. Search term is given by user through GUI interface and passed to search(term) function
2. 'index' is searched for existence of index[term] key
3. If found, the dictionary for 'links' in index[term].links is retrieved<br>
a. This is a list of the URL's containing this search term
4. URL's are sorted by 'score'
5. Top 10 URL's are returned

## Joining Parsed Document into the Index File
So when a user enters a query that is not in the index file. The program would need to navigate and search through all the files in the 
Corpus being <strong>WEBPAGES_CLEAN</strong>. So in <em>CorpusParser.py</em>, a new object of type <strong>DbEntry</strong> will be 
made. Objects of this type contain the document objects to be passed to <em>SearchEngine.py</em> as well as other fields needed to 
create and connect to the local database and to make the phrase into a search token (like making it lowercase,stripping out whitespace 
characters etc.) as well as methods to parse through a file and update the document object and save to the database. The tokenizing is 
done by <strong>nltk library</strong>. The document object is stored in DbEntry's `.queryDocument` field which is the same document that 
will be retrieved if queried from database.

Once the object is ready to be added to the index in <strong>SearchEngine.py</strong>. The document whether being passed from a DbEntry or retrieved from the database will be passed into `parseDoc(document_obj)` with the definition as follows:
```python
def parseDoc(document):
    searchTerm = document["query"] ### All the info objects being created will be associated to the document's query term
    ##scores = document["scores"] ##Extra field to add for ranking later
    ##doc_freq = document["document_frequency"] ##Once again something to consider for scoring later
    infoList = [] ### Info Objects are associations of (a single query, a single file, a single url)
    ####             So we can make many info Objects from one Term document since it contains ALL the file matches
    idfScore = IndexWeights.getIdfScore(CorpusParser.DOCUMENT_TOTAL,document["document_frequency"]) ## idfScore only depends on term's 
   	 ##frequency to the Whole Collection of files so only needs to be calculated once as long as document frequency is up-to-date
    index = 0 ## To iterate through score list, all the files and urls correspond
    for fileObject in document["file_matches"]:     ### Iterate through all the files that have the query in it
        fileName = fileObject["file_name"] 
        urlName = fileObject["file_url"]
        baseScore = document["scores"][index][fileName] ##Get the fileName's tf Score
        tfDf = baseScore * idfScore ## Calculate tfDf score now that idf Score is available
        newInfo = Info(searchTerm,fileName,tfDf,urlName) ## Make a new info object
        newInfo.count = document["count"] ## Updates its count to match the document's count of terms
        newInfo.priority = document["priority"] ## Update it to have the count of each html tags it matched to
        infoList.append(newInfo) ## Add to list
        index += 1
    return infoList ## Return List
```
Once the Info Objects have been returned from `parseDoc` the index can be updated by just following the example in Miguel's file
Example Code:
```python
termObjects = parseDoc(termDocumentObject)
for info in termObjects:
	infoToMap(info) ##Update the index objects of SearchEngine.py with newly created Info object from parseDoc
writeToFile()   ##Update the index File 
loadFromFile()  
```

## Document Template
When a file is parsed through a large <em>dictionary object</em> will be made of the form like this for now:
```python
document_template = 
{  "query": "search_term", 
   "priority": {"h1": 5,"h2": 4, "h3": 6,"title": 2,"b": 4,"strong": 12},
   "tagSum": 33,
   "tagRanking" : 123, ## This number would be determined by the frequency of each type of tag it was in, each one having a different 				##weight number
   "count": 456,    ## Total amount of times it has been encountered from searching all the file so far
   "document_frequency": 2,
   "scores": [{"0/1":12}, {"0/101",4.56}],
   		## The score a document,query pair is product of term-frequency-weight with its document frequency weight. The formula 
		## is on the lecture 12 slides.
   "current_rank": 3 ,
   		##Computed from scores above not sure how to implement, it is in lecture 13 slides, will likely be calculated once
   		## all files or a large number of files have been parsed
   "file_info": [{"file_name":"0/1","url":"www.ics.uci.edu/~ejw/pres/stc-99/sld009.htm","line_encountered":[1,4,55,66,101]},		
   		 {"file_name": "0/101","url":"cbcl.ics.uci.edu/doku.php/software/arem?do=login&sectok=dd041326677606876341a676d7ce3884",
		 	"lines_encountered":[4,5,67,89]}]
  ## To find out which file matches which url just look through bookkeeping.json
}
```

## Setup
How to <a href="http://api.mongodb.com/python/current/tutorial.html" target="_blank">link a Python Script to a MongoDB Database</a>

Use a library called <strong>pymongo</strong> to do this, I installed on a Python version 3.5, not sure if it will work with Python 2 
but since this project can be done purely offline and does not use <em>spacetime-crawler</em>, Python 2.7 is likely not necessary.

To install through pip open a terminal and type
```
python -m pip install pymongo
```
First, if your MongoDB server is on localhost turn it on with a terminal using
For Windows:
```
cd %MONGO_INSTALLATION_PATH%
mongod.exe --dbpath %MONGO_DATA_DIRECTORY_PATH%
```
Once on in Python to connect use 
```python
from pymongo import MongoClient
import json
from pprint import pprint
from bson import ObjectId
HOST = "localhost"
PORT = 27017
client = MongoClient(HOST,PORT) ## Establish connection
database = client["Name_of_your_db_to_use"] ## Choose database
chosenCollection = database.collection_to_use ## Use collection name in place of collection_to_use
docs = chosenCollection.find({})
for doc in docs: 
	pprint(doc)  ### Display all document entries in the collection
#### To update an existing document
post = chosenCollection.find_one({"name":"old_doc"})
post["name"] = "new_doc"
chosenCollection.save(post)
```

## Mapping files to URL's 
In the file, `bookkeeping.json` all the urls are matched into their correpsonding files in <strong>WEBPAGES_CLEAN</strong> as key, value
pairs. When doing a search this will be the starting point of the iteration as we when we create the <strong>document object</strong> to 
put into the database we will have the url to map through the file as we iterate and parse it, looking for the search term. To be able 
to extract and use the json in python use:
```python
import json
json_file = open("WEBPAGES_CLEAN/bookkeeping.json","r")
json_content = json_file.read()
json_file.close()
json_obj = json.loads(json_content) ## JSON is now a python dictionary object that can queried and iterated over.
```

## HTML Parsing
<a href="https://www.crummy.com/software/BeautifulSoup/bs4/doc/" target="_blank">BeautifulSoup4</a> for now is the best HTML Parser and handles the broken tag problem as mentioned in the write-up.
So for example a file of `someHTML.html`
```html
<html>
  <head>
  <title>Some title</title>
  </head>
  <body>
    <h1>Banner Header</h1>
    <strong>Boldfaced fonts </strong>
    <h3> A lower priority header</h3>
    <h3> Here is the broken tag
    <b>Some more bold faced sentences</b>
  </body>
 </html>  
 ```
when passed into BeautifulSoup through python and told to search for all <em>h3</em> tags. It will append a closing <em>"h3"</em> to the
somewhere in the document as shown:
```python
html_file = open("someHTML.html","r")
soup = BeautifulSoup(html_file.read(),"lxml")
html_file.close()
h3_list = soup.find_all('h3')
print(h3_list)
```
output:
```
[<h3> A lower priority header</h3>, <h3> Here is the broken tag

		<h3> An h4 header </h3>
<b>Some more bold faced sentences</b>
</h3>, <h3> An h4 header </h3>]
```
If you want to clean it up some more this function: 
```python
##### Usually the broken tag will be text that ends with the starting tag of another html element
#### To if an element in soup's findlist has a length > 1, than it might contain a broken tag
def check_if_clean(tagList):
    count = -1
    for i in tagList:
        count += 1
        if len(i.contents) > 1:
            tagList[count] = i.contents[0]
check_if_clean(h3_list)
print(h3_list)
```
output: 
```
[<h3> A lower priority header</h3>, ' Here is the broken tag\n\n\t\t', <h3> An h4 header </h3>]
```
NOTE: This function could filter out nested content as `<h3>Bold<b>STARTS HERES</b>andd ENDS</h3>` but all tags included in the corpus
`<title></title><h1></h1><h2></h2><h3></h3><strong></strong><b></b>` will be checked in soup.find_all(tag) statements so priority can be 
determined.
