# CS121-Corpus-Parse
CS 121 Collaborative Project

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
