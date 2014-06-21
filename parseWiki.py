#!/usr/bin/env python

import urllib
import argparse
from HTMLParser import HTMLParser

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'li':
            for attr in attrs:
                if attr[0] == 'class':
                    print attr[1]
        if tag == 'span':
            for attr in attrs:
                if attr[1] == 'toctext':
                    print attr[1]
    # def handle_endtag(self, tag):
    #     print "Encountered an end tag :", tag
    # def handle_data(self, data):
    #     print "Encountered some data  :", data

# instantiate the parser and fed it some HTML
HTMLparser = MyHTMLParser()

parser = argparse.ArgumentParser(description="Extract SKOS taxonomies from Wikipedia pages")
parser.add_argument('--input', '-i',
                    help = "URL of the source Wikipedia page", 
                    required = True)

args = parser.parse_args()

response = urllib.urlopen(args.input)
html = response.read()

HTMLparser.feed(html)

# print html
