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

BeautifulSoup4 for now is the best HTML Parser and handles the broken tag problem as mentioned in the write-up.
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
