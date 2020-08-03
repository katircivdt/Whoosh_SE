# The following code import data from the html files provided to us in a csv table
# containing just the fields we are interested in from the html file: the user must provide this information
# and the path to the folder containing the html files to run the code.

import os
import sys
import csv
from bs4 import BeautifulSoup

if len(sys.argv) < 4:
    sys.exit('\nInputError: the user must enter the html tags that he wants to consider as columns of the csv file,'
             'the number of the files to parse  and the path of the first html file.\n'
             'EX: "title body 1400 ./part_1/Cranfield_DATASET/DOCUMENTS/______1.html"\n')

tags = sys.argv[1:-2]      # we take the infos needed from the command line
N = int(sys.argv[-2])
path = sys.argv[-1]

if os.path.basename(path) != '______1.html':
    sys.exit('\nValueError: the last term of the input string must be the first html file to parse.\n'
             'EX: "./part_1/Cranfield_DATASET/DOCUMENTS/______1.html"\n')

csv_dir_path = os.path.dirname(os.path.dirname(path))     # we obtain the right path where save the csv file

field_names = ['id'] + tags

with open( csv_dir_path + '/docs_table.csv', 'w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=field_names)
    writer.writeheader()

    for id in range(1, N+1):
        file_path = csv_dir_path + '/DOCUMENTS/______'+str(id)+'.html'

        with open(file_path, 'r') as doc:
            soup = BeautifulSoup(doc, 'html.parser')

        tmp_dict = {'id': str(id)}
        for tag in tags: tmp_dict[tag] = soup.find(tag).text

        with open(file_path, 'r') as doc:
            soup = BeautifulSoup(doc, 'html.parser')

            writer.writerow(tmp_dict)