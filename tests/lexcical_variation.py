import unittest
import spacy
import numpy as np
from essay_evaluation.lexical_variation import LexicalVariationFeatures
from essay_evaluation.lexical_sophistication import LexicalSophisticationFeatures
from essay_evaluation.lexical_density import LexicalDensityFeatures
from essay_evaluation.lexical_accuracy import LexicalAccuracy, CollocationPreprocessor
from essay_evaluation.collocational_aspects import CollocationalAspects
from essay_evaluation.pipeline import FeatureCollector
from essay_evaluation.lexical_accuracy import SpellChecker, CollocationDectector, CollocationEvaluator
from essay_evaluation.formative_feedback_evaluator import FormativeFeedbackEvaluator

class TestLexicalVariation(unittest.TestCase):

    def setUp(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.nlp.remove_pipe('tagger')
        self.nlp.remove_pipe('parser')
        self.nlp.remove_pipe('ner')

        lexical_variation = LexicalVariationFeatures()
        self.nlp.add_pipe(lexical_variation, name=lexical_variation.name, last=True)

    def test_feature_values(self):
        text = """
            Why don't you buy that red hut. I think you should buy that orange summer skirt. The orange summer skirt is nice and is cheap. How about the purple top? The purple top expensive. The red hut is cheap.
        """.strip()

        doc = self.nlp(text)
        self.assertEqual(doc._.features_lv[0], 40) # 40 tokens by lexicalrichness

class TestSystem(unittest.TestCase):

    def test_system(self):
        #create pipeline elements
        lvf = LexicalVariationFeatures()
        lsf = LexicalSophisticationFeatures()
        ldf = LexicalDensityFeatures()
        sc = SpellChecker()
        cp = CollocationPreprocessor()
        cd = CollocationDectector()
        ce = CollocationEvaluator()
        laf = LexicalAccuracy()
        caf = CollocationalAspects()
        collector = FeatureCollector()

        #create pipeline
        nlp = spacy.load("en_core_web_sm")
        nlp.add_pipe(lvf, name="lexical_variation", last=True)
        nlp.add_pipe(lsf, name="lexical_sophistication", last=True)
        nlp.add_pipe(ldf, name="lexical_density", last=True)
        nlp.add_pipe(sc, name="checker", last=True)
        nlp.add_pipe(cp, name="collocation_preprocessor", last=True)
        nlp.add_pipe(cd, name="collocation_detector", last=True)
        nlp.add_pipe(ce, name="collocation_evaluator", last=True)
        nlp.add_pipe(laf, name="lexical_accuracy", last=True)
        nlp.add_pipe(caf, name="collocational_aspects", last=True)
        nlp.add_pipe(collector, name="collector", last=True)

        sampleTxt = "This is just some random text"

        doc = nlp(sampleTxt)

        feature_matrix = collector.get_feature_matrix()
        feature_matrix = np.array(feature_matrix)

        self.assertEqual(feature_matrix.shape[1], 35)

        #feedback
        ffe = FormativeFeedbackEvaluator()
        feedback = ffe(feature_matrix, "a1")
        feedback = np.array(feedback)
        self.assertEqual(feedback.shape[0], 12)
