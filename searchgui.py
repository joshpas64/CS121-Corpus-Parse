'''
Created on May 29, 2017

@author: cs
'''
from tkinter import *
import webbrowser
from SearchEngine import search, loadFromFile, score
import IndexWeights

class Interface(object):
    
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.root = None
        self.resultrow = 0
        self.resultcolumn = 0
        self.mainIndex = loadFromFile()[0]
        self.mainIndex = score(self.mainIndex)
    
    def launch(self):
        self.root = Tk()
        
        self.root.title("Awesome Shiny Search Engine")
        self.root["padx"]= 30
        self.root["pady"]=20
        self.root.geometry("800x600")
        
        
        # create all of the main containers
        self.top_frame = Frame(self.root, bg='cyan', width = 450, height=100, pady=3)
        self.btm_frame = Frame(self.root, bg='lavender', width = 450, height = 500, pady=3)

        # layout all of the main containers
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.top_frame.grid(row=0, sticky="ew")
        self.btm_frame.grid(row=1, sticky="ewn")
        # create the widgets for the top frame
        queryLabel = Label(self.top_frame, text="search box: ")
        self.queryEntry = Entry(self.top_frame, width=50)
        self.queryEntry.bind("<Return>", lambda e: self.doSearch())
        
        # layout the widgets in the top frame
        queryLabel.grid(row = 0, columnspan = 5)
        self.queryEntry.grid(row = 0, column = 6)
        
        
        # create entry Widget for writing search query
        """
        self.panedWindow = PanedWindow(master= self.root, orient=VERTICAL,borderwidth=1)
        self.panedWindow.pack(fill=BOTH, expand=1)
        
        queryLabel = Label(self.panedWindow, text="query box")
        self.panedWindow.add(queryLabel)
        self.queryEntry = Entry(self.panedWindow)
        self.queryEntry.bind("<Return>", lambda e: self.doSearch())
        self.panedWindow.add(self.queryEntry)
        
        bottom = Label(self.panedWindow, text="Results")
        self.panedWindow.add(bottom)
        """
         
    # Code to add widgets will go here...
        self.root.mainloop()
        
    
    def doSearch(self):
        self.resultrow =0
        queryString = self.queryEntry.get() 
        self.queryEntry.delete(0, END)
        queryToken = IndexWeights.makeSearchToken(queryString) ##Format string into token that normalizes into lowercase and puts phrases into an MWE
                                                        ## that makes it easier for them to search through. Phrases INITIALLY use a boolean type - search from
                                                        ## the nltk.MWETokenizer library
        # clear the results frame
        self.btm_frame.destroy()
        self.btm_frame = Frame(self.root, bg='lavender', width = 450, height = 500, pady=3)
        self.btm_frame.grid(row=1, sticky="ewn")
        # do the search here
        results = search(queryToken,self.mainIndex) ## Do the search with the token rather than the string to get consistent results
        print (len(results))
        # for each result element in the result obj, create a link 
        if len(results)>0:
            
            for result in results:
                link = Label(self.btm_frame, text="{url}".format(url=result.name), fg="blue", cursor="hand1")
                link.grid(row=self.resultrow)
                link.bind("<Button-1>", lambda e: self.openPage(result.name, e))
                self.resultrow +=1
                ##Retrieve data from result
                ##currentUrl = result.name
                ##currentFile = result.fileName 
                ##link.bind("<Button-1>", lambda e: self.openPage(currentUrl))
        else:
            link = Label(self.btm_frame, text="{url}".format(url="no results found"), fg="blue", cursor="hand2")
            link.grid(row=self.resultrow)
            #self.mainIndex = updateIndex.runQuery(queryString)
            #print("Index has been updated, please run query again!!")
                
    def openPage(self, url, event):
        try:
            webbrowser.open_new(event.widget["text"])
        except:
            print ("caught")
if __name__ == "__main__":
    gui = Interface()
    gui.launch()
