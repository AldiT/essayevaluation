import sys
import os
import numpy as np
import pandas as pd

from essay_evaluation.pipeline import Pipeline


if __name__ == "__main__":
    print('-------------Starting the extractor code-------------')
    #sys.stdout = open("output_log_pipeline.txt", 'w')

    pipeline = Pipeline()
    pipeline.association_scores()

    flip_path = "/home/aldit/flip_clean.csv"

    #Extract the essays from th e flip dataset.
    print('Extracting essays from the dataset....')
    essays = pd.read_csv(flip_path)['Essay']
    essays = essays[:2]
    assert(len(essays) != 0)
    
    
    matrix, docs = pipeline.pipe(essays, n_process=1)

    

    np.save('milestone/final.npy', matrix)


    print('-------------Ending the extractor code-------------')