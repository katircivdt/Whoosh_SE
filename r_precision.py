import utils
import pandas as pd
from whoosh import index
from whoosh import qparser
from whoosh import scoring
import numpy as np
import sys

def read_top5(path):
## Top-5 MRR score table created by MRR.py
## with read-top5 function we read MRR.tsv
## and returns 2 list. First one Method of Analyzer.. Second one scoring function to be used
	analyzer_top_five=[]
	scoring_func_top_five=[]
	df=pd.read_csv(path+"/MRR.tsv",sep=",").head()
	for analyzer,scoring in df["SE configuration"].str.split("_"):
		analyzer_top_five.append(analyzer)
		scoring_func_top_five.append(scoring)
	return (analyzer_top_five,scoring_func_top_five)

def Rprecision(queries,ground_truth,top_5_table):
## This function takes the queries , which have the groun truth values
## For each Analyzer method and scoring function find the result queries
## In result queries, there are as much as length of ground_truth resulting query
## Finally it compares ground_truth with resul queries and save the resul for
##  each Analyzer_Scoring rprecission values for each query stored in final_result_dict

	final_result_dict={}
	for Analyzer,Scoring_Function in zip(top_5_table[0],top_5_table[1]):
		ix = index.open_dir(path+Analyzer+"Analyzer")
		scoring_function=getattr(scoring, Scoring_Function)()
		analyzer_result={}
		for q_id in queries:
			query=queries[q_id]
			max_number_of_results = len(ground_truth[q_id])
			fields = ix.schema.names()
			fields.remove('id')
			qp = qparser.MultifieldParser(fields, ix.schema)
			parsed_query = qp.parse(query)

			# qp = qparser.QueryParser("body", ix.schema)
			# parsed_query = qp.parse(query)  # parsing the query

			searcher = ix.searcher(weighting=scoring_function)
			results = searcher.search(parsed_query, limit=max_number_of_results)
			final_result = []
			for result in results:
				if int(result["id"]) in gt[q_id]:
					final_result.append(1)
			analyzer_result[q_id] = sum(final_result) / len(ground_truth[q_id])
		final_result_dict["_".join([Analyzer,Scoring_Function])]=analyzer_result
		searcher.close()
	return final_result_dict


def Table_converter(rpression_result,saving_location):
## Converting rprecision values for each Analyzer_Scoring r-precission values into dataframe
	df=pd.DataFrame(columns=["Conf","MEAN","MIN","1°_quartile","MEDIAN","3°_quartile","MAX"])
	for idx,algorthims in enumerate(rpression_result):
		result_of_algo=np.array(sorted(rpression_result[algorthims].values()),dtype=np.float32)
		df.loc[idx]= [algorthims,
			 np.mean(result_of_algo),
			 np.min(result_of_algo),
			 np.quantile(result_of_algo,q=0.25),
			 np.median(result_of_algo),
			 np.quantile(result_of_algo,q=0.75),
			 np.max(result_of_algo)]

	df.to_csv(saving_location+"RprecisionTable.tsv",sep="\t",index = False)
	print(df)
	return df


user_input=int(input("Welcome to R-Precision distribution table module...\n \
Available Datasets are shown below: \n 1:Time_DATASET \n 2:Cranfield_DATASET: \n !!!!You have to choose th number of Dataset!!! "))
if user_input == 1:
##############################################################################################################################
	path=r"C:/Users/vedat/Desktop/Courses/DMT/homework/DMT/HW_1/part_1/part_1/Time_DATASET/"
	gt=utils.GroundTruth(r"C:\Users\vedat\Desktop\Courses\DMT\homework\DMT\HW_1\part_1\part_1\Time_DATASET\time_Ground_Truth.tsv")
	q=utils.QueryCollection(r"C:\Users\vedat\Desktop\Courses\DMT\homework\DMT\HW_1\part_1\part_1\Time_DATASET\time_Queries.tsv")
	last_query=utils.QueryInGroundTruth(q,gt)
##############################################################################################################################
elif user_input ==2 :
	path=r"C:\Users\vedat\Desktop\Courses\DMT\homework\DMT\HW_1\part_1\part_1\Cranfield_DATASET/"
	gt=utils.GroundTruth(r"C:\Users\vedat\Desktop\Courses\DMT\homework\DMT\HW_1\part_1\part_1\Cranfield_DATASET\cran_Ground_Truth.tsv")
	q=utils.QueryCollection(r"C:\Users\vedat\Desktop\Courses\DMT\homework\DMT\HW_1\part_1\part_1\Cranfield_DATASET\cran_Queries.tsv")
	last_query=utils.QueryInGroundTruth(q,gt)
else:
	sys.exit("You Mistype The Dataset number. Now module is terminated.")

Table_converter(Rprecision(last_query,gt,read_top5(path)),path)