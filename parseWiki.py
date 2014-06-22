#!/usr/bin/env python

import urllib
import argparse
import json
from HTMLParser import HTMLParser

# The extracted taxonomy goes into a dict
taxonomy = {}

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    titleFound = False
    entryFound = False
    currentList = 0
    previousLevel = 0
    currentLevel = 0
    currentData = None
    parentStack = []

    def handle_starttag(self, tag, attrs):
        if tag == 'li':
            if not attrs:
                self.entryFound = True
        if tag == 'h1' or tag == 'h2' or tag == 'h3' or tag == 'h4' or tag == 'h5' or tag == 'h6':
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
        if tag == 'h1' or tag == 'h2' or tag == 'h3' or tag == 'h4' or tag == 'h5' or tag == 'h6':
            self.titleFound = False

    def handle_data(self, data):
        if self.titleFound:
            self.currentData = data
            print self.currentLevel
            print self.parentStack[-1]
            print self.currentData
            if not self.parentStack[-1] in taxonomy:
                taxonomy[self.parentStack[-1]] = []
            taxonomy[self.parentStack[-1]].append(self.currentData)
            self.titleFound = False
        if self.currentList and self.entryFound:
            self.currentData = data
            print self.currentLevel
            print self.parentStack[-1]
            print self.currentData
            if not self.parentStack[-1] in taxonomy:
                taxonomy[self.parentStack[-1]] = []
            taxonomy[self.parentStack[-1]].append(self.currentData)
            self.entryFound = False
  


parser = argparse.ArgumentParser(description="Extract SKOS taxonomies from Wikipedia pages")
parser.add_argument('--input', '-i',
                    help = "URL of the source Wikipedia page", 
                    required = True)

args = parser.parse_args()

response = urllib.urlopen(args.input)
html = response.read()

# instantiate the parser and fed it some HTML
HTMLparser = MyHTMLParser()

HTMLparser.feed(html)

# print html

print(json.dumps(taxonomy, indent=4))
