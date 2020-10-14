import spacy
import sys
import time
import numpy as np
from tqdm import tqdm
from spacy.tokens import Doc
import neuralcoref
from essay_evaluation.lexical_density import LexicalDensityFeatures
from essay_evaluation.lexical_accuracy import SpellChecker, CollocationPreprocessor, CollocationDetector, CollocationEvaluator, LexicalAccuracy
from essay_evaluation.lexical_variation import LexicalVariationFeatures, IsRepetition
from essay_evaluation.lexical_sophistication import LexicalSophisticationFeatures
from essay_evaluation.lexical_density import LexicalDensityFeatures
from essay_evaluation.collocational_aspects import CollocationalAspects
from essay_evaluation.association_scores import AssociationScores
from essay_evaluation.lexical_variation_taaled import TaaledTokenClassifier, LexicalAccuracyTaaled, \
    LexicalVariationTaaled


class FeatureCollector(object):
    """
    This class can be used to retrieve a list of feature vectors of all documents.
    Add an instance of this class to the spacy pipeline. After processing all documents get_feature_matrix can be
    called in order to get the features of all documents in a single matrix.
    """
    name = "feature_collector"

    def __init__(self):
        self.feature_matrix = []
        if not Doc.has_extension("features"):
            Doc.set_extension("features", default=[])

    def __call__(self, doc):
        #put the row on the matrix
        feature_row = []

        # Some feature extraction classes might not have been added to the pipeline.
        # So we should only collect the features which have been extracted.
        if Doc.has_extension('features_lv'):
            feature_row += doc._.features_lv
        if Doc.has_extension('features_ls'):
            feature_row += doc._.features_ls
        if Doc.has_extension('features_la'):
            feature_row += doc._.features_la
        if Doc.has_extension('features_ca'):
            feature_row += doc._.features_ca
        if Doc.has_extension('features_ld'):
            feature_row += doc._.features_ld
        if Doc.has_extension('association_scores_mean'):
            feature_row += doc._.association_scores_mean
        if Doc.has_extension('association_scores_min'):
            feature_row += doc._.association_scores_min
        if Doc.has_extension('association_scores_max'):
            feature_row += doc._.association_scores_max


        # todo: collect features of new feature extractors
        # if Doc.has_extension('features_XX'):
        #     feature_row += doc._.features_XX

        self.feature_matrix.append(feature_row)

        # it's useful to have access to the feature vector
        # at document level
        doc._.features = feature_row
        return doc

    def get_feature_matrix(self):
        """

        :return:
        """
        return self.feature_matrix

    def reset(self):
        self.feature_matrix = []


class Pipeline:
    """An example docstring for a class definition."""

    def __init__(self, model="en_core_web_sm"):
        #Full or empty? doc.features
        self.pipeline = spacy.load(model)
        #add more stuff?

    modified = False

    def __call__(self, text):
        return self.pipeline(text)


    """
    Depending on the spacy version we could put batch_size or n_process to use for parallel
    processing, but since this is ambiguous and could cause errors, for now I will leave it unspecified.
    The user will have to use get_pipe and do that manually if that is crucial to his/her usecase.
    """
    def pipe(self, texts, as_tuples=False, disable=[], save_period=50, 
            save_to=''):

        feature_matrix = list()

        cycle_cnt = 0
        docs = []
        for doc in self.pipeline.pipe(texts, as_tuples=as_tuples, disable=disable):
            docs.append(doc)
            feature_matrix = list(feature_matrix)
            feature_matrix.append(list(doc._.features.values()))
            #save partial progress
            if cycle_cnt % save_period == 0 and cycle_cnt != 0:
                feature_matrix = np.array(feature_matrix)
                timestamp = str(time.time())
                np.save(save_to + timestamp + '.npy', feature_matrix)

            cycle_cnt += 1
            yield doc

        return feature_matrix, docs
    
    def get_pipe(self):
        return self.pipeline

    def _feature_collector(self):
        pass

    def spell_checker(self):
        if not self.pipeline.has_pipe(SpellChecker.name):
            sc = SpellChecker()
            self.pipeline.add_pipe(sc, name=SpellChecker.name, last=True)
            self.modified = True
        return self
    
    def lexical_variation(self):
        if not self.pipeline.has_pipe(LexicalVariationFeatures.name):
            lv = LexicalVariationFeatures()
            self.pipeline.add_pipe(lv, name=LexicalVariationFeatures.name, last=True)
            self.modified = True
        return self

    def lexical_sophistication(self):
        if not self.pipeline.has_pipe(LexicalSophisticationFeatures.name):
            ls = LexicalSophisticationFeatures()
            self.pipeline.add_pipe(ls, name=LexicalSophisticationFeatures.name, last=True)
            self.modified = True
        return self

    def lexical_density(self):
        if not self.pipeline.has_pipe(LexicalDensityFeatures.name):
            ld = LexicalDensityFeatures()
            self.pipeline.add_pipe(ld, name=LexicalDensityFeatures.name, last=True)
            self.modified = True
        return self

    def _collocation_preprocessor(self):
        self.spell_checker()
        if not self.pipeline.has_pipe(CollocationPreprocessor.name):
            cp = CollocationPreprocessor()
            self.pipeline.add_pipe(cp, name=CollocationPreprocessor.name, last=True)
            self.modified = True
        return self

    def collocation_detector(self):
        self._collocation_preprocessor()
        if not self.pipeline.has_pipe(CollocationDetector.name):
            cd = CollocationDetector()
            self.pipeline.add_pipe(cd, name=CollocationDetector.name, last=True)
            self.modified = True
        return self

    def collocation_evaluator(self):
        self.collocation_detector()
        if not self.pipeline.has_pipe(CollocationEvaluator.name):
            ce = CollocationEvaluator()
            self.pipeline.add_pipe(ce, name=CollocationEvaluator.name, last=True)
            self.modified = True
        return self
    
    def collocational_aspects(self):
        self.collocation_evaluator()
        if not self.pipeline.has_pipe(CollocationalAspects.name):
            ca = CollocationalAspects()
            self.pipeline.add_pipe(ca, name=CollocationalAspects.name, last=True)
            self.modified = True
        return self

    def lexical_accuracy(self):
        self.collocation_evaluator()
        if not self.pipeline.has_pipe(LexicalAccuracy.name):
            la = LexicalAccuracy()
            self.pipeline.add_pipe(la, name=LexicalAccuracy.name, last=True)
            self.modified = True
        return self

    def association_scores(self):
        self.collocation_evaluator()
        if not self.pipeline.has_pipe(AssociationScores.name):
            ass = AssociationScores()
            self.pipeline.add_pipe(ass, name=AssociationScores.name, last=True)
            self.modified = True
        return self

    def taaled_token_classifier(self):
        if not self.pipeline.has_pipe(TaaledTokenClassifier.name):
            ttc = TaaledTokenClassifier()
            self.pipeline.add_pipe(ttc, name=TaaledTokenClassifier.name, last=True)
        return self

    def lexical_variation_taaled(self):
        self.taaled_token_classifier()
        if not self.pipeline.has_pipe(LexicalVariationTaaled.name):
            lv = LexicalVariationTaaled()
            self.pipeline.add_pipe(lv, name=LexicalVariationTaaled.name, last=True)
        return self

    def neuralcoref(self):
        if not self.pipeline.has_pipe('neuralcoref'):
            neuralcoref.add_to_pipe(self.pipeline)
        return self
    
    def repetition_detector(self):
        self.neuralcoref()
        if not self.pipeline.has_pipe(IsRepetition.name):
            ir = IsRepetition()
            self.pipeline.add_pipe(ir, name=IsRepetition.name)
        return self

    #add more methods

    def __str__(self, ):
        return '< Pipeline object; name:' + FeatureCollector.name + ' Pipeline components: ' + self.pipeline.pipeline + '>'


if __name__ == "__main__":
    pipe = Pipeline()

    sample_text = "Aldi Topalli is coding the pipeline right now! He is one of the best programmers we have!"

    pipe.lexical_variation()
    doc1 = pipe(sample_text)

    print(doc1._.features_lv)

    pipe.lexical_sophistication()

    doc2 = pipe(sample_text)

    print(doc2._.features_ls)
    
