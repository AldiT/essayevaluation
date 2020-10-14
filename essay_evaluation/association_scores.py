import spacy
import os
import numpy as np
import csv
import pandas as pd

from spacy.tokens import Doc
from essay_evaluation.database import get_driver
from essay_evaluation.legacy.collocation_detection import getPOSTag, getHeadPOSDepRelDepPOS
from essay_evaluation.lexical_accuracy import SpellChecker, CollocationPreprocessor, CollocationDectector, CollocationEvaluator, Collocation
from neo4j import Session
from neo4j import GraphDatabase



##Pipeline imports 


from essay_evaluation.lexical_variation import LexicalVariationFeatures
from essay_evaluation.lexical_sophistication import LexicalSophisticationFeatures
from essay_evaluation.lexical_density import LexicalDensityFeatures
from essay_evaluation.lexical_accuracy import LexicalAccuracy
from essay_evaluation.collocational_aspects import CollocationalAspects
from essay_evaluation.lexical_accuracy import SpellChecker
from essay_evaluation.lexical_accuracy import CollocationPreprocessor, CollocationDectector, CollocationEvaluator


##



import argparse

from scipy.special import factorial


class DatabaseManager:
    non_zero_const = 0.0000000000000000000000000000000001
    
    def __init__(self, url='bolt://localhost:7687', username='neo4j', password='elia.2018'):
        print('Creating driver')
        self._driver = get_driver()#GraphDatabase.driver(url, auth=(username, password))
        
    def close(self):
        self._driver.close()

    def get_os(self, collocations):
        lst_converted = [{'lempos1': col.lempos1, 'lempos2': col.lempos2, 'type': col.type} for col in collocations]

        with self._driver.session()  as session:
            self.o11s = []
            self.o12s = []
            self.o21s = []
            self.o22s = []


            for item in session.write_transaction(self._get_o11, lst_converted):
                self.o11s.append(item['freq_o11'])

            for item in session.write_transaction(self._get_o12, lst_converted):
                self.o12s.append(item['freq_o12'])
            
            for item in session.write_transaction(self._get_o21, lst_converted):
                self.o21s.append(item['freq_o21'])
            
            for item in session.write_transaction(self._get_o22, lst_converted):
                overall_freq = item['freq_o22']
            self.o22s = np.ones(len(self.o11s)) * overall_freq

            self.o11s = np.array(self.o11s)
            self.o12s = np.array(self.o12s)
            self.o21s = np.array(self.o21s)
            self.o22s = np.array(self.o22s)


            self.o12s = self.o12s - self.o11s
            self.o21s = self.o21s - self.o11s
            self.o22s = self.o22s - self.o11s

            #Add the constant for numerical stability
            self.o11s = self.o11s + self.non_zero_const
            self.o12s = self.o12s + self.non_zero_const
            self.o21s = self.o21s + self.non_zero_const
            self.o22s = self.o22s + self.non_zero_const

        self.get_e11()
        self.get_e12()
        self.get_e21()
        self.get_e22()

        self.Ns = self.o11s + self.o12s + self.o21s + self.o22s

    def _get_o11(self, tx, collocations):
        query_O11 = """
            UNWIND {collocations} AS c
            OPTIONAL MATCH (u:Word:EN {lempos: c.lempos1})<-[r:COLLOCATES_WITH]-(v:Word:EN {lempos: c.lempos2}) 
            RETURN SUM(r.raw_freq) as freq_o11, c
        """
        return tx.run(query_O11, {"collocations": collocations})

    def _get_o12(self, tx, collocations):
        query_O12 = """
            UNWIND {collocations} AS c
            OPTIONAL MATCH (u:Word:EN {lempos: c.lempos1})<-[r:COLLOCATES_WITH]-(v:Word:EN) 
            RETURN SUM(r.raw_freq) as freq_o12, c
        """
        return tx.run(query_O12, {"collocations": collocations})

    def _get_o21(self, tx, collocations):
        query_O12 = """
            UNWIND {collocations} AS c
            OPTIONAL MATCH (u:Word:EN)<-[r:COLLOCATES_WITH]-(v:Word:EN {lempos: c.lempos2})
            RETURN SUM(r.raw_freq) as freq_o21, c
        """
        return tx.run(query_O12, {"collocations": collocations})
    def _get_o22(self, tx, collocations):
        query_O22 = """
            MATCH (:Word:EN)<-[r:COLLOCATES_WITH]-(:Word:EN)
            RETURN SUM(r.raw_freq) as freq_o22
        """
        return tx.run(query_O22, {"collocations": collocations})

    def get_e11(self):
        if type(self.o11s) == None or type(self.o12s) == None or type(self.o21s) == None or type(self.o22s) == None:
            return
        self.e11s = ((self.o11s+self.o12s)*(self.o11s+self.o21s)) / (self.o11s + self.o12s + self.o21s + self.o22s)
    
    def get_e12(self):
        if type(self.o11s) == None or type(self.o12s) == None or type(self.o21s) == None or type(self.o22s) == None:
            return
        self.e12s = ((self.o11s+self.o12s)*(self.o12s+self.o22s)) / (self.o11s + self.o12s + self.o21s + self.o22s)


    def get_e21(self):
        if type(self.o11s) == None or type(self.o12s) == None or type(self.o21s) == None or type(self.o22s) == None:
            return
        self.e21s = ((self.o21s+self.o22s)*(self.o11s+self.o21s)) / (self.o11s + self.o12s + self.o21s + self.o22s)

    def get_e22(self):
        if type(self.o11s) == None or type(self.o12s) == None or type(self.o21s) == None or type(self.o22s) == None:
            return
        self.e22s = ((self.o21s+self.o22s)*(self.o12s+self.o22s)) / (self.o11s + self.o12s + self.o21s + self.o22s)


class AssociationScores(object):
    name="association_scores"
    def __init__(self):

        if not Doc.has_extension("association_scores_mean"):
            Doc.set_extension("association_scores_mean", default=[])
        if not Doc.has_extension("association_scores_min"):
            Doc.set_extension("association_scores_min", default=[])
        if not Doc.has_extension("association_scores_max"):
            Doc.set_extension("association_scores_max", default=[])

        print('Created inside AssociationScores.')
        self.database_manager = DatabaseManager()
    
    def __call__(self, doc):
        #self.database_manager = DatabaseManager()

        self.database_manager.get_os(doc._.collocations)

        np.seterr(divide="ignore")

        doc._.association_scores_mean = self.get_association_scores_mean()
        doc._.association_scores_min = self.get_association_scores_min()
        doc._.association_scores_max = self.get_association_scores_max()
        np.seterr(divide="warn")
        #self.database_manager.close() ##Close the connection with the db
        return doc

    def get_association_scores_mean(self):
        lstAssocScores = []

        mi = self.get_mi_score()
        mi3 = self.get_mi3_score()
        #simple_ll = self.get_simple_ll()
        t_score = self.get_t_score()
        z_score = self.get_z_score()
        chi_square = self.get_chi_squared_test()

        lstAssocScores.append(np.mean(mi[np.invert(np.isnan(mi)) ]))
        lstAssocScores.append(np.mean(mi3[np.invert(np.isnan(mi3)) ]))
        #lstAssocScores.append(np.mean(simple_ll[np.invert(np.isnan(simple_ll)) ]))   ##The problem is that we get numerical overflow here.
        lstAssocScores.append(np.mean(t_score[np.invert(np.isnan(t_score)) ]))
        lstAssocScores.append(np.mean(z_score[np.invert(np.isnan(z_score)) ]))
        lstAssocScores.append(np.mean(chi_square[np.invert(np.isnan(chi_square))]))
        
        return lstAssocScores

    def get_association_scores_min(self):
        lstAssocScores = []

        mi = self.get_mi_score()
        mi3 = self.get_mi3_score()
        #simple_ll = self.get_simple_ll()
        t_score = self.get_t_score()
        z_score = self.get_z_score()
        chi_square = self.get_chi_squared_test()
        
        #print(np.isnan(mi))

        lstAssocScores.append(np.min(mi[np.invert(np.isnan(mi)) ]))
        lstAssocScores.append(np.min(mi3[np.invert(np.isnan(mi3)) ]))
        #lstAssocScores.append(np.min(simple_ll[np.invert(np.isnan(simple_ll)) ]))   ##The problem is that we get numerical overflow here.
        lstAssocScores.append(np.min(t_score[np.invert(np.isnan(t_score)) ]))
        lstAssocScores.append(np.min(z_score[np.invert(np.isnan(z_score)) ]))
        lstAssocScores.append(np.min(chi_square[np.invert(np.isnan(chi_square))]))
        
        return lstAssocScores
    
    def get_association_scores_max(self):
        lstAssocScores = []

        mi = self.get_mi_score()
        mi3 = self.get_mi3_score()
        #simple_ll = self.get_simple_ll()
        t_score = self.get_t_score()
        z_score = self.get_z_score()
        chi_square = self.get_chi_squared_test()

        lstAssocScores.append(np.max(mi[np.invert(np.isnan(mi)) ]))
        lstAssocScores.append(np.max(mi3[np.invert(np.isnan(mi3)) ]))
        #lstAssocScores.append(np.max(simple_ll[np.invert(np.isnan(simple_ll)) ]))   ##The problem is that we get numerical overflow here.
        lstAssocScores.append(np.max(t_score[np.invert(np.isnan(t_score)) ]))
        lstAssocScores.append(np.max(z_score[np.invert(np.isnan(z_score)) ]))
        lstAssocScores.append(np.max(chi_square[np.invert(np.isnan(chi_square))]))
        
        return lstAssocScores

    def get_mi_score(self):
        return np.log(self.database_manager.o11s/self.database_manager.e11s)

    def get_mi3_score(self):
        return np.log(np.power(self.database_manager.o11s, np.full(self.database_manager.o11s.shape, 3)) / self.database_manager.e11s)

    def get_t_score(self):
        return (self.database_manager.o11s - self.database_manager.e11s) / np.sqrt(self.database_manager.o11s)


    def get_z_score(self):
        return (self.database_manager.o11s - self.database_manager.e11s)/np.sqrt(self.database_manager.e11s)
    
    def get_chi_squared_test(self):
        return ((self.database_manager.o11s - self.database_manager.e11s)**2/self.database_manager.e11s + (self.database_manager.o12s - self.database_manager.e12s)**2/self.database_manager.e12s
            + (self.database_manager.o21s - self.database_manager.e21s)**2/self.database_manager.e21s + (self.database_manager.o22s - self.database_manager.e22s)**2/self.database_manager.e22s
        )

        
    #multinomial likelihood
    ##Not used due to numerical overflow, and other numerical problems
    def get_simple_ll(self):
        
        coefficient = np.log(factorial(self.database_manager.Ns)/np.power(self.database_manager.Ns, self.database_manager.Ns))
        print('Coefficient: ', coefficient)
        nominant = (
                np.log(np.power(self.database_manager.e11s, self.database_manager.o11s))
                * np.log(np.power(self.database_manager.e12s, self.database_manager.o12s))
                * np.log(np.power(self.database_manager.e21s, self.database_manager.o21s))
                * np.log(np.power(self.database_manager.e22s, self.database_manager.o22s))
        ) 
        print("Nominant value: ", nominant)
        determinant = (
            np.log(factorial(self.database_manager.o11s))
            * np.log(factorial(self.database_manager.o12s))
            * np.log(factorial(self.database_manager.o21s))
            * np.log(factorial(self.database_manager.o22s))
        )
        print("Determinant value: ", determinant)

        return coefficient * (nominant/determinant)
        """
        ( (factorial(self.database_manager.Ns)/np.power(self.database_manager.Ns, self.database_manager.Ns)) #N!/N^N

                * 
                (
                      (np.power(self.database_manager.e11s, self.database_manager.o11s))
                    * (np.power(self.database_manager.e12s, self.database_manager.o12s))
                    * (np.power(self.database_manager.e21s, self.database_manager.o21s))
                    * (np.power(self.database_manager.e22s, self.database_manager.o22s))
                ) 
                / 
                (
                      factorial(self.database_manager.o11s)
                    * factorial(self.database_manager.o12s)
                    * factorial(self.database_manager.o21s)
                    * factorial(self.database_manager.o22s)
                )
                )
        """

    def __del__(self):
        self.database_manager.close()


def get_flip_texts(filepath):
    texts = []
    with open(filepath) as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            texts.append(row['Essay'].replace('\n', ' '))
    return texts


##Testing the script
if __name__ == "__main__":
    from essay_evaluation.pipeline import FeatureCollector
    import time
    import sys
    sys.stdout = open('extraction_logs.txt', 'w')

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Text file relative location.")
    parser.add_argument("--flip", help="The path to the csv containing the data for the flip dataset")
    args = parser.parse_args()
    path = args.file
    flip_path = args.flip

    nlp = spacy.load("en_core_web_sm")
    print("Model loaded, creating pipeline...", flush=True)

    #create pipeline elements
    #lvf = LexicalVariationFeatures()
    #lsf = LexicalSophisticationFeatures()
    #ldf = LexicalDensityFeatures()
    sc = SpellChecker()
    cp = CollocationPreprocessor()
    cd = CollocationDectector()
    ce = CollocationEvaluator()
    #laf = LexicalAccuracy()
    caf = CollocationalAspects()
    ass = AssociationScores()
    collector = FeatureCollector()

    #create pipeline
    
    #nlp.add_pipe(lvf, name="lexical_variation", last=True)
    #nlp.add_pipe(lsf, name="lexical_sophistication", last=True)
    #nlp.add_pipe(ldf, name="lexical_density", last=True)
    nlp.add_pipe(sc, name="checker", last=True)
    nlp.add_pipe(cp, name="collocation_preprocessor", last=True)
    nlp.add_pipe(cd, name="collocation_detector", last=True)
    nlp.add_pipe(ce, name="collocation_evaluator", last=True)
    #nlp.add_pipe(laf, name="lexical_accuracy", last=True)
    #nlp.add_pipe(caf, name="collocational_aspects", last=True)
    nlp.add_pipe(ass, name="association_scores", last=True)
    nlp.add_pipe(collector, name="collector", last=True)

    ##association score
    print("Pipeline created, reading file...", flush=True)

    txt_file = open(flip_path, "r")
    txt = txt_file.read()
    print("File read, passing to spacy pipeline...", flush=True)

    #doc = nlp(txt)

    #print("Number of collocations: ", len(doc._.collocations))
    #print("o11s: ", ass.database_manager.o11s)
    #print("Association scores: ")
    #print(doc._.association_scores_mean)
    #print(doc._.association_scores_min)
    #print(doc._.association_scores_max)
    

    print("--------Extracting multiple documents feature--------", flush=True)

    #Read documents into an array
    
    essay_df = pd.read_csv(flip_path)
    essays = list(essay_df["Essay"])
    #essays = essays[:2]
    #essays.append('')
    #print(essays, flush=True)
    print("Essays read successfully...", flush=True)
    
    docs = []
    idxs = []
    for idx, essay in enumerate(essays):
        print("Essay number: ", idx, flush=True)
        try:
            docs.append(nlp(essay))
            idxs.append(idx)
        except ValueError as ve:
            print('Value Error: ', ve)
            docs.append(None)
            idxs.append(-1)
            as_scores = collector.get_feature_matrix()
            np.save("scores.npy", as_scores)
            np.save("idxs.npy", idxs)
        except Exception as e:
            print('Generic error: ', e, flush=True)
            docs.append(None)
            idxs.append(-1)
            as_scores = collector.get_feature_matrix()
            np.save("scores.npy", as_scores)
            np.save("idxs.npy", idxs)


    print("Extraction complete...", flush=True)

    as_scores = collector.get_feature_matrix()
    print("Scores from collector: \n", as_scores, flush=True)
    #print("Scores from doc: \n", np.concatenate((doc._.association_scores_mean, doc._.association_scores_min, doc._.association_scores_max)))
    np.save("scores.npy", as_scores)
    np.save("idxs.npy", idxs)
    print("Scores saved", flush=True)
    #print(as_scores)

    print("--------End of extraction--------")
