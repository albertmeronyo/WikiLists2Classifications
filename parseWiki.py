#!/usr/bin/env python

import urllib
import argparse
import json
from HTMLParser import HTMLParser

# The extracted taxonomy goes into a dict
class Taxonomy:
    def __init__(self):
        self.taxonomy = {}

    def addEntry(self, parent, child):
        if not parent in self.taxonomy:
            self.taxonomy[parent] = []
        self.taxonomy[parent].append(child)

    def layout(self):
        print(json.dumps(self.taxonomy, indent=4))        

# create a subclass and override the handler methods
class TaxonomyHTMLParser(HTMLParser):
    def __init__(self, __taxonomy):
        HTMLParser.__init__(self)
        self.titleFound = False
        self.entryFound = False
        self.currentList = 0
        self.previousLevel = 0
        self.currentLevel = 0
        self.currentData = None
        self.parentStack = []
        self.taxonomy = __taxonomy

    def handle_starttag(self, tag, attrs):
        if tag == 'li':
            if not attrs:
                self.entryFound = True
        if self.isHeader(tag):
            self.titleFound = True
            self.previousLevel = self.currentLevel
            self.currentLevel = int(tag[-1])
            if self.currentLevel > self.previousLevel:
                self.parentStack.append(self.currentData)
        if tag == 'ul':
            self.currentList += 1
            self.currentLevel += 1
            self.parentStack.append(self.currentData)
                    
    def handle_endtag(self, tag):
        if tag == 'ul':
            self.currentList -= 1
            self.currentLevel -= 1
            self.parentStack.pop()
        if self.isHeader(tag):
            self.titleFound = False

    def handle_data(self, data):
        if self.titleFound:
            self.currentData = data
            if not self.isUninteresting(self.parentStack[-1]):
                self.taxonomy.addEntry(self.parentStack[-1], self.currentData)
            self.titleFound = False
        if self.currentList and self.entryFound:
            self.currentData = data
            if not self.isUninteresting(self.parentStack[-1]):
                self.taxonomy.addEntry(self.parentStack[-1], self.currentData)
            self.entryFound = False

    def isHeader(self, tag):
        return tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')

    def isUninteresting(self, data):
        return data in ('Content', 'Navigation menu', 'See also')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract SKOS taxonomies from Wikipedia pages")
    parser.add_argument('--input', '-i',
                    help = "URL of the source Wikipedia page", 
                    required = True)
    
    args = parser.parse_args()

    response = urllib.urlopen(args.input)
    html = response.read()

    taxonomy = Taxonomy()

    # instantiate the parser and fed it some HTML
    HTMLparser = TaxonomyHTMLParser(taxonomy)
    HTMLparser.feed(html)

    # print html
    taxonomy.layout()

