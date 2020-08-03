# The following code allow us to create an empty index according to a certain schema
# that is built starting from the fields contained in the csv file we have created.
# So the user has just to pass in input the analyzer he wants implement and the path
# to the csv documents collection csv file.

import os
import sys
import csv
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.analysis import SimpleAnalyzer, StandardAnalyzer, StemmingAnalyzer, FancyAnalyzer

if len(sys.argv) != 3:
    sys.exit('\nInputError: the user must enter an analyzer and the csv file path to index.\n'
             'EX: "SimpleAnalyzer ./part_1/Cranfield_DATASET/docs_table.csv"\n\n'
             'The user can choose from the following analyzer methods:\n\n'
             '"SimpleAnalyzer": it is a lower case filter\n\n'
             '"StandardAnalyzer": it is a lower case filter and  stop-words filter\n\n'
             '"StemmingAnalyzer": it is a lower case filter, stop-words filter and stemming filter\n\n'
             '"FancyAnalyzer": it is a lower case, stop-words, stemming filter and split words into subwords when it'
             'is useful\n')

with open(sys.argv[2], 'r') as csv_file:
    reader = csv.reader(csv_file, delimiter=' ')
    schema_fields = next(reader)[0].split(',')

if sys.argv[1] == 'SimpleAnalyzer': analyzer = SimpleAnalyzer()
elif sys.argv[1] == 'StandardAnalyzer': analyzer = StandardAnalyzer()
elif sys.argv[1] == 'StemmingAnalyzer': analyzer = StemmingAnalyzer()
elif sys.argv[1] == 'FancyAnalyzer': analyzer = FancyAnalyzer()

schema = Schema(id=ID(stored=True))
for field in schema_fields[1:]:
    schema.add(field, TEXT(stored=False, analyzer=analyzer))

index_dir = os.path.dirname(sys.argv[2]) + '/' + sys.argv[1]
os.mkdir(index_dir)
create_in(index_dir, schema)