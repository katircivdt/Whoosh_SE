# This code fills the index we have built with the empty_index.py script.
# The user must pass to this script from the terminal command line both the path of
# the documents csv table and the empty index folder.

import sys
import csv
from whoosh import index

if len(sys.argv) != 3:
    sys.exit('InputError: the user must enter the csv file path and the index directory path\n'
             'EX: "./part_1/Cranfield_DATASET/docs_table.csv ./part_1/Cranfield_DATASET/SimpleAnalyzer"\n')

index_dir = sys.argv[2]
ix = index.open_dir(index_dir)

writer = ix.writer(procs=2, limitmb=500)

docs = sys.argv[1]
file = open(docs, "r", encoding='latin1')
csv_reader = csv.reader(file, delimiter=',')
csv_reader.__next__()

num_fields = len(ix.schema.names())

if num_fields == 2:

    for record in csv_reader:
        id = record[0]
        body = record[1]

        writer.add_document(id=id, body=body)

elif num_fields  == 3:

    for record in csv_reader:
        id = record[0]
        title = record[1]
        body = record[2]

        writer.add_document(id=id, title=title, body=body)

writer.commit()
file.close()