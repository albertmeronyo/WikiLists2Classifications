WikiLists2SKOS
==============

A supervised extractor of SKOS taxonomies from lists in Wikis

## Why this?

HTML renders of Wiki sites (like Wikipedia articles) contain sometimes
concept taxonomies represented as nested lists, like the following:

- https://en.wikipedia.org/wiki/List_of_genres
- https://en.wikipedia.org/wiki/List_of_religions_and_spiritual_traditions

In such pages, titles of sections play the role of top categories of a
concept scheme. Lists contained in such sections generally enumerate
subconcepts of these top categories, and sometimes even nested lists
repersent subsubconcepts of these subconcepts.

For programs processing Semantic Web data, representing these
taxonomies as RDF SKOS is much more convenient than the human-tailored
HTML.

## So what does it do?

[WikiLists2SKOS](http://github.com/albertmeronyo/WikiLists2SKOS) is a
Python script that reads a target URL, processes its HTML, looks for
lists contained under section headers, generates the correspondent RDF
SKOS taxonomy, and serializes it into a destination Turtle file.

Currently, only Wikipedia HTML layouting is supported.

## How to use it?

Type

`./parseWiki.py -i http://foo/bar -o foobaz.ttl`

in your favourite shell.

## Dependencies

- Python 2.7.5
- [RDFLib](https://github.com/RDFLib)
- [lxml](http://lxml.de/)

## Credits

Author: [Albert Meroño-Peñuela](http://github.com/albertmeronyo)

License: [LGPL v3.0](http://www.gnu.org/licenses/lgpl.html)

