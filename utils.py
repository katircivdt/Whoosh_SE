# This script contains all the functions that we used in MRR.py and top-5.py scripts.

import csv
import numpy as np
import math
from collections import defaultdict
from whoosh import index
from whoosh.qparser import *
from whoosh import scoring
from whoosh.qparser import MultifieldParser
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure


# the following function imports data from the ground truth set of queries
def GroundTruth(ground_path):

    ground = defaultdict(list)

    with open(ground_path, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        reader.__next__()

        for row in reader:
            ground[int(row[0])].append(int(row[1]))

    return ground


# the following function imports data from the whole queries collection we have
def QueryCollection(query_path):

    query = defaultdict(str)

    with open(query_path) as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        reader.__next__()

        for row in reader:
            query[int(row[0])] = row[1]

    return query


# the following function performs an "intersection" between the ground truth set of queries
# and the whole set of queries... it will return the queries that are contained in the
# ground truth
def QueryInGroundTruth(query_collection, ground_truth):

    query_in_ground = {}

    for query in query_collection:
        if ground_truth.get(query) != None: query_in_ground[query] = query_collection[query]

    return query_in_ground


# given a SE configuration (analyzer and scoring function), this function will return
# the MRR value for that configuration
def MRR(queries, ground, score, ix):

    MRR_table = {}

    fields = ix.schema.names()     # opening the schema fields
    fields.remove('id')            # we are not interested in the 'id' field for the MRR evaluation

    RR_sum = 0

    for query in queries:
        RR = 0
        qp = MultifieldParser(fields, ix.schema)
        parsed_query = qp.parse(queries[query])

        searcher = ix.searcher(weighting=score)
        results = searcher.search(parsed_query, limit=None)

        for doc in results:
            if int(doc['id']) in ground[query]:   # we just stop the loop for the first relevant result
                K = doc.rank + 1                  # and we evaluate the single RR
                RR = 1/K
                break

        RR_sum += RR         # summing the RR for the singular query

    MRR = RR_sum/len(ground)     # evaluating the average on the available queries
    return MRR


# given a SE configuration (analyzer and scoring function), this function will return
# the P@K and the nDCG list of values obtained averaging on the ground truth queries on
# the set of K levels proposed
def nDCG_and_PatK(queries, ground, score, k_levels, ix):

    precision_on_collection = []
    nDCG_collection = []

    fields = ix.schema.names()
    fields.remove('id')

    for query in queries:
        precision_on_query = []
        nDCG = []

        qp = MultifieldParser(fields, ix.schema)
        parsed_query = qp.parse(queries[query])
        searcher = ix.searcher(weighting=score)

        for k in k_levels:
            n_relevant_docs = 0
            DGain = 0
            IdealDGain = 0
            results = searcher.search(parsed_query, limit=k)
            K = min(len(ground[query]), k)    # we normalize the P@K measure by the min between the
                                              # relevant result of that G-T query and the level K
            for doc in results:
                IdealDGain += 1/math.log2(doc.rank+2)    # we have to take in consideration the ideal case
                                                         # to normalize the DCG in the right way
                if int(doc['id']) in ground[query]:
                    n_relevant_docs += 1
                    DGain += 1/math.log2(doc.rank+2)     # there is a +2 because the formula need a +1 for
                                                         # the log() and the .rank counter starts from 0
            precision_on_query.append(n_relevant_docs/K)
            nDCG.append(DGain/IdealDGain)

        precision_on_collection.append(precision_on_query)
        nDCG_collection.append(nDCG)

    p_at_k = np.sum(precision_on_collection, axis=0)/len(precision_on_collection)  # evaluating the average on 
    Mean_nDCG = np.sum(nDCG_collection, axis=0)/len(nDCG_collection)               # the available queries

    results = [p_at_k, Mean_nDCG]
    return list(np.round(results, decimals=3))


# the following function make the plot for P@K
def plot_MAP(results, figure_path, dataset):

    figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    ax = plt.gca()
    ax.tick_params(axis='both', which='major', labelsize=12)
    plt.xlabel('$K$', fontsize=16)
    plt.ylabel('MAP', fontsize=16)
    plt.title('Mean average precision at $K$ for '+dataset, fontsize=16)
    for conf in results:
        plt.plot([1,3,5,10], results[conf], label=conf, linestyle='-', marker='o')
    plt.legend()
    plt.savefig(figure_path)


# the following function make the plot for nDCG
def plot_nDCG(results, figure_path, dataset):

    figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    ax = plt.gca()
    ax.tick_params(axis='both', which='major', labelsize=12)
    plt.xlabel('$K$', fontsize=16)
    plt.ylabel('nDCG', fontsize=16)
    plt.title('nDCG average at $K$ for '+dataset, fontsize=16)
    for conf in results:
        plt.plot([1,3,5,10], results[conf], label=conf, linestyle='-', marker='o')
    plt.legend()
    plt.savefig(figure_path)