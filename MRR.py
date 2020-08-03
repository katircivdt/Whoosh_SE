# This script performs the MRR evaluation for each SE configurations we have considered.
# The user must enter just the directory containing the data, then a MRR csv
# file will be saved into the same directory.

import os
import sys
import csv
import pandas as pd
from whoosh import index
from whoosh.qparser import *
from whoosh import scoring
from whoosh.qparser import MultifieldParser
import utils

if len(sys.argv) != 2:

    sys.exit('\nInputError:The user must enter the data directory on which he want implement the MRR.\n'
             'EX: .../part1/Cranfield_DATASET\n')

data_dir = sys.argv[1]

analyzers = {'Simple': data_dir + '/SimpleAnalyzer',
             'Standard': data_dir + '/StandardAnalyzer',
             'Stemming': data_dir + '/StemmingAnalyzer',
             'Fancy': data_dir + '/FancyAnalyzer'}

scoring_functions = ['BM25F', 'TF_IDF', 'Frequency', 'PL2']

if os.path.basename(data_dir) == 'Cranfield_DATASET':      # we just keep all the paths that we need for the
    ground_path = data_dir + '/cran_Ground_Truth.tsv'      # chosen dataset
    query_path = data_dir + '/cran_Queries.tsv'

elif os.path.basename(data_dir) == 'Time_DATASET':
    ground_path = data_dir + '/time_Ground_Truth.tsv'
    query_path = data_dir + '/time_Queries.tsv'

ground_truth = utils.GroundTruth(ground_path)       # importing the ground truth
query_coll = utils.QueryCollection(query_path)       # importing the query collection
query_ground = utils.QueryInGroundTruth(query_coll, ground_truth)    # taking the queries that are contained in
                                                                     # the ground truth

MRRtable = {}
i = 0

# we perform the MRR evaluation for each analyzer and each scoring function we have considered

for analyzer in analyzers:
    ix = index.open_dir(analyzers[analyzer])

    for score in scoring_functions:
        scoring_function = getattr(scoring, score)()

        # MRR evaluation for the single analyzer and scoring function in the loop
        MRRtable[i] = {'SE configuration': analyzer+'_'+score,
                           'MRR': round(utils.MRR(query_ground, ground_truth, scoring_function, ix), 3)}


        i += 1

# using a pandas dataframe to export the result in an ordered MRR csv table

df_MRR = pd.DataFrame.from_records(MRRtable).T.sort_values('MRR', axis=0, ascending=False)
df_MRR.set_index('SE configuration', inplace=True)
df_MRR.to_csv(data_dir + '/MRR.tsv')