import os
import warnings

import hunspell
from spacy.tokens import Doc
import re
import spacy
import sys
from essay_evaluation import FeaturePipelineComponent
from essay_evaluation.legacy.contractions import expand_contractions
from essay_evaluation.legacy.collocation_detection import getPOSTag, getHeadPOSDepRelDepPOS
from essay_evaluation.database import get_driver, get_collocation_metric
from neo4j import Session


class Collocation:

    def __init__(self, lempos1='', lempos2='', type='', metric=None):
        self.lempos1 = lempos1
        self.lempos2 = lempos2
        self.type = type
        self.metric = metric

    def __str__(self):
        if self.metric is not None:
            return self.lempos1 + '<--[ (' + str(round(self.metric, 2)) + ') ]--' + self.lempos2
        return self.lempos1 + '<--[ (X) ]--' + self.lempos2


def get_hunspell_default():
    return get_hunspell()


def get_hunspell(lang='en_US'):
    if sys.platform.startswith("darwin"):
        # mac os
        dict_file = '/Library/Spelling/' + lang + '.dic'
        affixes_file = '/Library/Spelling/' + lang + '.aff'
    else:
        # other
        dict_file = '/usr/share/hunspell/' + lang + '.dic'
        affixes_file = '/usr/share/hunspell/' + lang + '.aff'
    if not os.path.isfile(dict_file):
        raise Exception("could not create spell checker - dictionary " + str(lang) + " is not installed")
    return hunspell.HunSpell(dict_file, affixes_file)


class SpellChecker:
    """
    SpellChecker is a spaCy pipeline component which  adds a spell_errors extension to the spaCy document class. The
    extensions contains a list of spelling mistakes found by the hunspell spell checker.
    """
    name = "SpellChecker"

    def __init__(self, hunspell_objects=[]):
        if not hunspell_objects:
            hunspell_objects = [get_hunspell('en_US'), get_hunspell('en_GB')]

        self.hunspell_objects = hunspell_objects
        self.token_pattern = re.compile("^[A-Za-z]+$")

        if not Doc.has_extension("spell_errors"):
            Doc.set_extension("spell_errors", default=[])

    def __call__(self, doc):
        if not doc.is_nered:
            warnings.warn('The spaCy document has not named entities tagged! Please add the NER component or else the '
                          'spellchecker might detected named entities as spelling mistakes.', Warning)

        # if the NER is missing the t.ent_type will always be zero
        doc._.spell_errors = [t for t in doc if t.ent_type == 0 and self.token_pattern.match(str(t).strip())
                              and not self.is_correct_spelled(str(t))]
        return doc

    def is_correct_spelled(self, token):
        """
        Returns whether the token is spelled correctly. This is the case if any of the initialized spell-checkers marks
        the word as correct.
        :param token:
        :return:
        """
        for hobj in self.hunspell_objects:
            if hobj.spell(str(token)):
                return True

        return False


class CollocationPreprocessor:
    name = "collocation_preprocessor"

    def __init__(self, hunspell_object=None):
        self.stopwords_list = [
            'the',
            'a',
            'an',
            'are',
            'on',
            'to',
            'at',
            'every',
            'this'
        ]

        if hunspell_object is None:
            hunspell_object = get_hunspell_default()

        self.hobj = hunspell_object

        self.nlp = spacy.load('en_core_web_lg')  # we need another spaCy model as we want to tag the document with
        # corrected spelling mistakes
        # Todo: maybe always do that at the beginning and just save the
        #       spelling mistakes

        if not Doc.has_extension("lstFilteredDepParseCorpus"):
            Doc.set_extension("lstFilteredDepParseCorpus", default=[])

    def __call__(self, doc):
        """
        original method: preprocess from collocation_error_detection.py
        :param doc:
        :return:
        """

        pre_processed_text = self.preprocess(doc.text)
        lstDepParseCorpus = self.getPOSTagDepParsedSent(pre_processed_text)
        doc._.lstFilteredDepParseCorpus = self.remove_stopwords(lstDepParseCorpus)
        return doc

    def preprocess(self, textCorpora):
        textCorpora = expand_contractions(textCorpora)

        pre_processed_text = self.spell_check(textCorpora)

        return pre_processed_text

    def getPOSTagDepParsedSent(self, doc):
        lstPOSTagDepParsedSent = []

        doc = self.nlp(doc)

        for token in doc:
            lstPOSTagDepParsedSent.append(
                (token.head.text, token.head.lemma_, token.head.tag_, token.dep_, token.text, token.lemma_, token.tag_))

        return lstPOSTagDepParsedSent

    def remove_stopwords(self, lstDepParseCorpus):

        lstFilteredDepParseCorpus = []

        for depRel in lstDepParseCorpus:
            headword = depRel[1]  # head lemma
            collocate = depRel[5]  # token lemma

            if self.stopwords_list.count(headword) > 0 or self.stopwords_list.count(
                    collocate) > 0 or collocate == '-PRON-':
                continue
            if headword == collocate:
                continue
            lstFilteredDepParseCorpus.append(depRel)

        return lstFilteredDepParseCorpus

    def spell_check(self, textCorpora):
        # return textCorpora
        words = textCorpora.split()
        spell_checked_text = ''

        for word in words:
            try:
                if self.hobj.spell(word) == False:
                    suggestions = self.hobj.suggest(word)
                    if len(suggestions) > 0:
                        # Get the one `most likely` answer
                        spell_checked_text += suggestions[0] + ' '
                    else:
                        spell_checked_text += word + ' '
                else:
                    spell_checked_text += word + ' '
            except UnicodeEncodeError:
                spell_checked_text += word + ' '
        return spell_checked_text


class CollocationDetector:
    name = "collocation_detector"

    def __init__(self):
        if not Doc.has_extension("collocations"):
            Doc.set_extension("collocations", default=[])

        self.lstColTypes = ['NOUN+VERB', 'NOUN+NOUN', 'ADJ+NOUN', 'VERB+NOUN', 'VERB+ADJ', 'VERB+VERB', 'ADV+VERB',
                            'ADV+toVERB', 'ADJ+toVERB', 'ADV+ADJ']

    def __call__(self, doc):
        doc._.collocations = self.find_all_collocations(doc)
        return doc

    def find_all_collocations(self, doc):
        """
        extracted from collocation_error_detection
        :param textCorpora:
        :param db:
        :return:
        """
        incorrect_collocations = {}
        collocation_list = []

        lstFilteredDepParseCorpus = doc._.lstFilteredDepParseCorpus

        for colType in self.lstColTypes:
            colType_errors_list = []
            lstheadPOSRelDepPOS = getHeadPOSDepRelDepPOS(colType)
            # todo: change how the getCollocations function work in order to remove the double loop
            for collocation in self.getCollocations(lstheadPOSRelDepPOS, lstFilteredDepParseCorpus):
                lempos1 = collocation[1] + '_' + getPOSTag(colType, collocation[2])
                lempos2 = collocation[5] + '_' + getPOSTag(colType, collocation[6])

                if type in ['VERB+ADJ', 'VERB+VERB', 'ADV+toVERB', 'ADJ+toVERB']:
                    # lempos1 <--[COLLOCATES_WITH]--lempos2
                    collocation_list.append(Collocation(lempos1, lempos2, colType))
                else:
                    # lempos2 <--[COLLOCATES_WITH]--lempos1
                    collocation_list.append(Collocation(lempos2, lempos1, colType))

        return collocation_list

    @staticmethod
    def getCollocations(lstheadPOSRelDepPOS, lstPOSTagDepParsedCorpora):
        lstCollocations = []
        for headPOSRelDepPOS in lstheadPOSRelDepPOS:
            headWordPOSTags = headPOSRelDepPOS[0]
            dependencyRelations = headPOSRelDepPOS[1]
            dependentPOSTags = headPOSRelDepPOS[2]

            for line in lstPOSTagDepParsedCorpora:
                if any(y == line[2] for y in headWordPOSTags) and any(
                        x == line[3] for x in dependencyRelations) and any(x == line[6] for x in dependentPOSTags):
                    lstCollocations.append(line)

        return lstCollocations


# deprecated - use CollocationDetector instead!
class CollocationDectector(CollocationDetector):
    name = "collocation_detector"


class CollocationEvaluator:
    """
    This component matches a detected collocation against the database.
    If the collocation is not found in the database if counts as error.
    It also stores the twf-metric for each collocation
    """
    name = "collocation_evaluator"

    def __init__(self):
        if not Doc.has_extension("collocation_errors"):
            Doc.set_extension("collocation_errors", default=[])

        if not Doc.has_extension("collocation_twf_values"):
            Doc.set_extension("collocation_twf_values", default=[])

    def __call__(self, doc):
        driver = get_driver()
        collocation_errors = []
        collocation_twf_values = []

        session: Session
        with driver.session() as session:
            get_collocation_metric(session, doc._.collocations)
            for collocation in doc._.collocations:
                if collocation.metric is None:
                    collocation_errors.append(collocation)
                else:
                    collocation_twf_values.append(collocation.metric)
        # driver.close()
        doc._.collocation_errors = collocation_errors
        doc._.collocation_twf_values = collocation_twf_values
        return doc


class LexicalAccuracy(FeaturePipelineComponent):
    name = "features_la"
    feature_names = [  # 'LA_E',
        'LA_ER', 'LA_COL_ERR_R']

    def __init__(self):
        super().__init__()
        if not Doc.has_extension("features_la"):
            Doc.set_extension("features_la", default=[])

    def __call__(self, doc):
        doc._.features_la = []
        doc._.features['LA_E'] = len(doc._.spell_errors)
        doc._.features['LA_ER'] = len(doc._.spell_errors) / len(doc)
        doc._.features['LA_COL_ERR_R'] = self.collocation_error_ratio(doc)

        # Deprecated! Use doc._.features instead
        # LV_E is not added due to a legacy issue with the FormativeFeatureEvaluator
        # (this binning indices are wrong otherwise)
        doc._.features_la.append(doc._.features['LA_ER'])
        doc._.features_la.append(doc._.features['LA_COL_ERR_R'])

        return doc

    @staticmethod
    def collocation_error_ratio(doc):
        coll_errors = len(doc._.collocation_errors)
        coll_total = len(doc._.collocations)

        if coll_total == 0:
            return 0
        return coll_errors / coll_total


if __name__ == '__main__':
    import sys
    import spacy

    if len(sys.argv) != 2:
        print("Usage: ", sys.argv[0], ' "this is a text"')
        sys.exit(1)

    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe(SpellChecker(), name=SpellChecker.name, last=True)
    nlp.add_pipe(CollocationPreprocessor(), name=CollocationPreprocessor.name, last=True)
    nlp.add_pipe(CollocationDetector(), name=CollocationDectector.name, last=True)
    nlp.add_pipe(CollocationEvaluator(), name=CollocationEvaluator.name, last=True)
    nlp.add_pipe(LexicalAccuracy(), name=LexicalAccuracy.name, last=True)
    doc = nlp(sys.argv[1])
    print("Spelling Mistakes", ', '.join(doc._.spell_errors))
    print("###")
    print("Collocations", ', '.join([str(c) for c in doc._.collocations]))
    print("###")
    for index, name in enumerate(LexicalAccuracy.feature_names):
        print(name, doc._.features_la[index])
