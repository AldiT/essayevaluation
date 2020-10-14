import numpy as np
import pandas as pd
import pickle
from essay_evaluation.pipeline import Pipeline
from essay_evaluation.classifier import Classifier

import sys

print(__file__)

try:
    sys.stdout = open("progress.txt", 'w')

    print("--------------------Extracting features--------------------", flush=True)
    print("Starting the extraction ...", flush=True)


    dataset_path = '/../../data/flip_new.csv'

    mutated_essays = np.load("../../data/mutated_essays.npy", allow_pickle=True)
    sent_indicies = np.load("../../data/sent_indicies.npy", allow_pickle=True)
    clause_indicies = np.load("../../data/clause_indicies.npy", allow_pickle=True)
    
    print("Creating the pipeline...", flush=True)
    pipeline = Pipeline().lexical_variation_taaled().get_pipe()
    # it would be nice if the classifier would be part of our Pipeline class. But it's not that simple because it has to 
    # be the _last_ component
    print("Pipeline created...", flush=True)
    print("Starting extraction...", flush=True)
    print("-----------------------------------------------", flush=True)
    feature_matrix = []
    for idx, row in enumerate(mutated_essays):
        print(f"Row: {idx}/488", flush=True)
        feature_row = []
        for mutation in row:
            feature_row.append(list(pipeline(mutation)._.features.values()))
        feature_matrix.append(feature_row)
    
    print("-----------------------------------------------", flush=True)

    feature_matrix = np.array(feature_matrix)
    np.save("../../data/feature_matrix.npy", feature_matrix)

    print("--------------------Finish--------------------", flush=True)
except Exception as e:
    print(e)
    np.save("../../data/feature_matrix.npy", feature_matrix)