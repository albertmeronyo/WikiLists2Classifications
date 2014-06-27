#!/usr/bin/env python

import urllib
import argparse
import logging
import re
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import Namespace, RDF, SKOS
from lxml import etree

class WikiLists2SKOS:
    TITLE_XPATH = '//h1/span[@dir="auto"][1]'
    WIKILISTS_XPATH = '/html/body/div[3]/div[2]/div[4]/h2/span[@class="mw-headline"] | /html/body/div[3]/div[2]/div[4]/h3/span[@class="mw-headline"] | /html/body/div[3]/div[2]/div[4]/h4/span[@class="mw-headline"] | /html/body/div[3]/div[2]/div[4]/h5/span[@class="mw-headline"] | /html/body/div[3]/div[2]/div[4]/h6/span[@class="mw-headline"] | /html/body/div[3]/div[2]/div[4]//ul/li[1] | /html/body/div[3]/div[2]/div[4]//ul/li/a[1]'
    namespaces = {
        'w2s':Namespace('http://example.org/w2s/resource/'),
        'skos':Namespace('http://www.w3.org/2004/02/skos/core#')
    }

    def __init__(self, __targetURL, __logLevel):
        self.log = logging.getLogger('WikiLists2SKOS')
        self.log.setLevel(__logLevel)

        self.log.info('Reading remote URL %s...' % args.input)
        self.html = urllib.urlopen(__targetURL).read()
        self.g = Graph()
        self.g.bind('skos', SKOS)        

    def toSKOS(self):
        root = etree.HTML(self.html)
        tree = etree.ElementTree(root)
        
        t = tree.xpath(self.TITLE_XPATH)
        conceptSchemeURI = self.namespaces['w2s'][self.URIzeString(t[0].text)]
        self.g.add( (conceptSchemeURI, RDF.type, SKOS.ConceptScheme) )
        self.g.add( (conceptSchemeURI, SKOS.prefLabel, Literal(t[0].text)) )

        r = tree.xpath(self.WIKILISTS_XPATH)
        for h in r:
            if h.text and len(h.text):
                conceptURI = self.namespaces['w2s'][self.URIzeString(h.text)]
                self.g.add( (conceptURI, RDF.type, SKOS.Concept) )
                self.g.add( (conceptURI, SKOS.prefLabel, Literal(h.text)) )
                self.log.debug('Category: %s' % h.text)
                parent = h.getparent().getparent().getparent()
                parentString = None
                if parent.tag == 'li':
                    self.log.debug('Parent: %s' % h.getparent().getparent().getparent()[0].text)
                    parentString = h.getparent().getparent().getparent()[0].text
                elif parent.tag == 'div' and parent.get('id') == 'mw-content-text':
                    cat = None
                    for child in parent:
                        if str(child.tag)[0] == 'h':
                            cat = child
                        if child == h.getparent().getparent():
                            break
                    self.log.debug('Parent: %s' % cat[0].text)
                    parentString = cat[0].text
                else:
                    self.log.debug("Couldn't find a parent for this category")
                parentURI = self.namespaces['w2s'][self.URIzeString(parentString)]
                self.g.add( (conceptURI, SKOS.broader, URIRef(parentURI)) )
                self.log.debug('---')

    def serialize(self, __file):
        outputFile = open(__file, 'w')
        turtle = self.g.serialize(None, format='turtle')
        outputFile.writelines(turtle)
        outputFile.close()

    def URIzeString(self, __nonuri):
        return urllib.quote(re.sub('\s|\(|\)|,|\.','_',unicode(__nonuri).strip()).encode('utf-8', 'ignore'))
    
if __name__ == "__main__":
    # Parse commandline arguments
    parser = argparse.ArgumentParser(description="Extract SKOS taxonomies from Wikipedia pages")
    parser.add_argument('--input', '-i',
                        help = "URL of the source Wiki page", 
                        required = True)
    parser.add_argument('--verbose', '-v',
                        help = "Be verbose -- debug logging level",
                        required = False, 
                        action = 'store_true')
    parser.add_argument('--output', '-o',
                        help = "Output filename",
                        required = True)
    args = parser.parse_args()

    # Logging
    
    logLevel = logging.INFO
    if args.verbose:
        logLevel = logging.DEBUG

    logging.basicConfig(level=logLevel)

    logging.info('Initializing...')
    converter = WikiLists2SKOS(args.input, logLevel)

    logging.info('Converting...')
    converter.toSKOS()

    logging.info('Serializing to output file %s' % args.output)
    converter.serialize(args.output)

    logging.info('Done.')
