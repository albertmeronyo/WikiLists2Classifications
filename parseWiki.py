#!/usr/bin/env python

import urllib
import argparse
import json
import logging
from rdflib import Graph
from HTMLParser import HTMLParser
from lxml import etree

# The extracted classification goes into a dict
class Classification:
    def __init__(self):
        self.idsToLabels = {}
        self.classification = {}
        self.depth = {}

    def addEntry(self, parent, child, depth):
        if not parent in self.classification:
            self.classification[parent] = []
        self.classification[parent].append(child)
        self.depth[parent] = depth
        self.depth[child] = depth + 1

    def getRoot(self):
        return self.classification[None][0]

    def layoutJSON(self):        
        print(json.dumps(self.classification, indent=4))

class ClassificationSerializer:
    def __init__(self, __classification):
        self.classification = __classification
        self.graph = Graph()

    def toSKOS(self):
        print 'toSKOS'

    def toQB(self):
        print 'toQB'
    
# create a subclass and override the handler methods
class ClassificationHTMLParser(HTMLParser):
    def __init__(self, __classification):
        HTMLParser.__init__(self)
        self.endParsing = False
        self.titleFound = False
        self.entryFound = False
        self.currentList = 0
        self.previousLevel = 0
        self.currentLevel = 0
        self.currentData = None
        self.parentStack = []
        self.classification = __classification

    def handle_starttag(self, tag, attrs):
        if tag == 'li':
            if not attrs:
                self.entryFound = True
        if self.isHeader(tag):
            self.titleFound = True
            self.previousLevel = self.currentLevel
            self.currentLevel = int(tag[-1])
            levelDiff = self.currentLevel - self.previousLevel
            if levelDiff > 0:
                self.parentStack.append(self.currentData)
            elif levelDiff < 0:
                self.parentStack.pop()
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
        if self.titleFound and not self.endParsing:
            self.currentData = data
            logging.debug(self.currentData)
            logging.debug(self.parentStack[-1])
            logging.debug(self.currentLevel)
            if not self.isUninteresting(self.parentStack[-1]) and not self.isUninteresting(self.currentData):
                self.classification.addEntry(self.parentStack[-1], self.currentData, self.currentLevel)
            self.titleFound = False
        if self.currentList and self.entryFound and not self.endParsing:
            self.currentData = data
            logging.debug(self.currentData)
            logging.debug(self.parentStack[-1])
            logging.debug(self.currentLevel)
            if not self.isUninteresting(self.parentStack[-1]) and not self.isUninteresting(self.currentData):
                self.classification.addEntry(self.parentStack[-1], self.currentData, self.currentLevel)
            self.entryFound = False

    def handle_comment(self, data):
        if data.find('parser cache') >= 0:
            self.endParsing = True

    def isHeader(self, tag):
        return tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')

    def isUninteresting(self, data):
        return data in ('Contents', 'Navigation menu', 'See also', 'External links', 'References')
    
if __name__ == "__main__":
    # Parse commandline arguments
    parser = argparse.ArgumentParser(description="Extract SKOS taxonomies from Wikipedia pages")
    parser.add_argument('--input', '-i',
                        help = "URL of the source Wikipedia page", 
                        required = True)
    parser.add_argument('--verbose', '-v',
                        help = "Be verbose -- debug logging level",
                        required = False, 
                        action = 'store_true')
    parser.add_argument('--format', '-f',
                        help = "Output format: SKOS, QB",
                        required = True,
                        choices = ['SKOS', 'QB'])
    parser.add_argument('--output', '-o',
                        help = "Output filename",
                        required = True)
    args = parser.parse_args()

    # Logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logging.info('Reading remote URL %s...' % args.input)
    response = urllib.urlopen(args.input)
    html = response.read()

    logging.info('Initializing local data structure...')
    classification = Classification()

    logging.info('Parsing HTML...')
    # instantiate the HTML parser
    HTMLparser = ClassificationHTMLParser(classification)
    HTMLparser.feed(html)


    logging.info('Doing lxml stuff...')
    tree = etree.HTML(html)

    # Title
    r = tree.xpath('//h1/span[@dir="auto"][1] | //h2/span[@class="mw-headline"] | //h3/span[@class="mw-headline"] | //ul/li | //ul/li/a[1]')
    for h in r:
        if h.text and len(h.text):
            print h.text


        

    logging.info('Converting to %s and serializing to %s...' % (args.format, args.output))
    converter = ClassificationSerializer(classification)
    if args.format == 'SKOS':
        converter.toSKOS()
    elif args.format == 'QB':
        converter.toQB()

    logging.info('Done.')
