# This script performs the P@K and nDCG evaluation for each SE configurations we have considered.
# The user must enter just the directory containing the data, then the P@K and nDCG plots are saved
# in the same directory.

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

# we import the MRR table to know the top-5 configurations of each
df_MRR = pd.read_csv(data_dir + '/MRR.tsv', index_col='SE configuration')


analyzers = {'Simple': data_dir + '/SimpleAnalyzer',
             'Standard': data_dir + '/StandardAnalyzer',
             'Stemming': data_dir + '/StemmingAnalyzer',
             'Fancy': data_dir + '/FancyAnalyzer'}


if os.path.basename(data_dir) == 'Cranfield_DATASET':       # we just keep all the paths that we need for the
    ground_path = data_dir + '/cran_Ground_Truth.tsv'       # chosen dataset
    query_path = data_dir + '/cran_Queries.tsv'

elif os.path.basename(data_dir) == 'Time_DATASET':
    ground_path = data_dir + '/time_Ground_Truth.tsv'
    query_path = data_dir + '/time_Queries.tsv'

ground_truth = utils.GroundTruth(ground_path)      # importing the ground truth
query_coll = utils.QueryCollection(query_path)      # importing the query collection
query_ground = utils.QueryInGroundTruth(query_coll, ground_truth)   # taking the queries that are contained in
                                                                    # the ground truth

conf_MAP = {}
conf_nDCG = {}
k_levels = [1, 3, 5, 10]        # the required K levels

for configuration in df_MRR.index[:5]:      # considering the top-5 configurations and loop on them
    analyzer_score = configuration.split('_')

    index_type = index.open_dir(analyzers[analyzer_score[0]])
    scoring_function = getattr(scoring, analyzer_score[1])

    # we are evaluating at the same time the P@K and the nDCG for a single configuration
    results = utils.nDCG_and_PatK(query_ground, ground_truth, scoring_function, k_levels, index_type)
    conf_MAP[configuration] = results[0]
    conf_nDCG[configuration] = results[1]

utils.plot_MAP(conf_MAP, data_dir + '/MAP.png', os.path.basename(data_dir))    # P@K plot
utils.plot_nDCG(conf_nDCG, data_dir + '/nDCG.png', os.path.basename(data_dir))   # nDCG plot