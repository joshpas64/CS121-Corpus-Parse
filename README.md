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

## Document Template
When a file is parsed through a large <em>dictionary object</em> will be made of the form like this for now:
```python
document_template = 
{  "query": "search_term", 
   "priority": {"h1": 5,"h2": 4, "h3": 6,"title": 2,"b": 4,"strong": 12},
   "tagSum": 33,
   "tagRanking" : 123, ## This number would be determined by the frequency of each type of tag it was in, each one having a different 
   		       ##weight number
   "count": 456,    ## Total amount of times it has been encountered from searching all the file so far
   "document_frequency": 2,
   "scores": [{"0/1":12}, {"0/101",4.56}],
   		## The score a document,query pair is product of term-frequency-weight with its document frequency weight. The formula 
		## is on the lecture 12 slides.
   "current_rank": 3 ,
   		##Computed from scores above not sure how to implement, it is in lecture 13 slides, will likely be calculated once
   		## all files or a large number of files have been parsed
		##File_info contains file-to-term related information.
		##Fields contain the file name, the tfScore which is related to the count of matching terms each document 
		## (log(1 + count)), a dictionary object representing the amount of times the term was within the specified tags
		## i.e. (title,h1,h2,h3,b,strong) 
		## It is all the items of the file_info list which will eventually, after some parsing and using the SearchEngine.py 
		## module, that will eventually be the values used in the inverted index. 
   "file_info": [{"file_name":"0/1","url":"www.ics.uci.edu/~ejw/pres/stc-99/sld009.htm","line_encountered":
   		  [1,4,55,66,101],"tags_encountered":{"title":1,"h1":0,"h2":0,"h3":2,"b":0,"strong":2},"tfScore":0.12345},		
   		 {"file_name": "0/101","url":"cbcl.ics.uci.edu/doku.php/software/arem?do=login&sectok=dd041326677606876341a676d7ce3884",
		 	"lines_encountered":[4,5,67,89],"tag_encountered":{"title":0,"h1":2,"h2":2,"h3":1,"b":1,"strong":
			5},"tfScore":0.42341}]
  ## To find out which file matches which url just look through bookkeeping.json
}
```

## Setup
Click <a href="https://www.mongodb.com/download-center" target="_blank">here</a> to install a local MongoDB database.
How to <a href="http://api.mongodb.com/python/current/tutorial.html" target="_blank">link a Python Script to a MongoDB Database</a>

Use a library called <strong>pymongo</strong> to do this, I installed on a Python version 3.5, not sure if it will work with Python 2 
but since this project can be done purely offline and does not use <em>spacetime-crawler</em>, Python 2.7 is likely not necessary.

To install through pip open a terminal and type
```
python -m pip install pymongo
```

Other libraries that are used that can be installed through pip if they are not already available to you:
Link to <a href="https://www.crummy.com/software/BeautifulSoup/bs4/doc/" target="_blank"> BeautifulSoup4 Documentation</a>
Link to <a href="http://www.nltk.org/" target="_blank">nltk Documentation</a>
```
python -m pip install jsonpickle
python -m pip install nltk
python -m pip install lxml
pythom -m pip install beautifulsoup4
```
<em>Note: </em> for <strong>NLTK</strong>, to have access to <em>all</em> libraries you must run a python shell and install them.
You only have to do this once, in the python shell type:
```
import nltk
nltk.download()
## After this an installation window prompt appears and asks which libraries you wish to install, I installed all of them by default
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

## Setting up the files on your local Computer
While any setup could work to have all the code in this repository run without having to modify any code, have all the python and index 
files all in the same directory and the folder that contains all the documents of the Corpus, `WEBPAGES_CLEAN` in this directory as well
This structure on your file system would work 
```
Inside of Search Engine project Folder: 
Below are the files and folders that should be listed
Files:
	CorpusParser.py
	SearchEngine.py
	IndexWeights.py
	searchgui.py
	indexJSON.txt
Folder: 
	WEBPAGES_CLEAN //Contains all the subfolders and files of the ics uci document collection (in total 37,000+ files)
```

## Some Notes on the GUI
So the template and the way the GUI works in <em>searchengine.py</em> is great. 
For the way the GUI responds to a query these events should occur:
1. Once the query has been recorded, the program will load the index file into an object variable that can be queried and processed
2. The indexFile (indexJSON.txt, a file containing a large JSON object in text form) has to be converted from text back into a JSON 
   Object that Python can use
3. To do this, a call to SearchEngine.loadFromFile() will likely have to be called but only once.
4. Once the index has been loaded into variable, let's call it indexDictionary, the GUI can just check if it is in the index.
5. Since it is a dictionary object, a simple if word in indexDictionary is likely all that's needed
6. If there's a match in the index, the program will return a list of objects from the index file that will be the top 10 best results 
   for the query.
7. From there each object should contain the fileName and url of the corresponding document.
8. Once the GUI has its top 10 result it can display the 10 Links
9. In terms of what should be displayed, probably only two things at most:
* A title that represents link that can be either be the content of `<title></title>` tags for that document or its starting lines
* A snipped below the title that could show the first 1 or 2 lines of the file that contain the search query, if possible the search 
  query, when rendered, can be in bold to show where it matches in the document.
This description sounds a bit vague likely because the final contents of the index file are still being worked on as well as the fact 
that the scoring implementation is still not finalized either.

All the person working on the GUI python file should worry about is just knowing how to access the index file and use or process its 
contents. All the information it will need should be in that file (indexJSON.txt), such as the results for a query 
and which ones to pick. 

The GUI code will likely need to import the other two processing files (SearchEngine.py and CorpusParser.py) so 
it can load the index and, in the case the query is not in the index file, execute a search through the whole collection parsing and 
checking every document in it, adding to the index file as it goes along and then requerying the index for the new results. The
functions and classes that do that will already be implemented in the above two files it will just need to call those methods properly.

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
<a href="https://www.crummy.com/software/BeautifulSoup/bs4/doc/" target="_blank">BeautifulSoup4</a> for now is the best HTML Parser and 
handles the broken tag problem as mentioned in the write-up.
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
