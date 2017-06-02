'''
Created on May 29, 2017

@author: cs
'''
from tkinter import *
import webbrowser
from SearchEngine import search

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
        queryString = self.queryEntry.get() 
        self.queryEntry.delete(0, END)
        # clear the results frame
        self.btm_frame.destroy()
        self.btm_frame = Frame(self.root, bg='lavender', width = 450, height = 500, pady=3)
        self.btm_frame.grid(row=1, sticky="ewn")
        # do the search here
        results = search(queryString)
        # for each result element in the result obj, create a link 
        for result in results:
            link = Label(self.btm_frame, text="{url}".format(url=result.name), fg="blue", cursor="hand2")
            link.grid(row=self.resultrow)
            link.bind("<Button-1>", lambda e: self.openPage(r"https://stackoverflow.com/questions/2260235/how-to-clear-the-entry-widget-after-a-button-is-pressed-in-tkinter"))

    def openPage(self, url):
        try:
            webbrowser.open_new(url)
        except:
            print ("caught")
if __name__ == "__main__":
    gui = Interface()
    gui.launch()