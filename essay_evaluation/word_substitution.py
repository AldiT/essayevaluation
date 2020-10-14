

import spacy
import numpy as np
import sys
import subprocess
import os
import pandas as pd
from time import gmtime, strftime
from spacy.tokens.doc import Doc
from spacy.tokens.token import Token
from essay_evaluation import FeaturePipelineComponent
from collections import OrderedDict

try:
    import spacy
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "spacy"])
    import spacy


from essay_evaluation.pipeline import Pipeline
from spacy.tokenizer import Tokenizer
from spacy.util import compile_infix_regex, compile_prefix_regex, compile_suffix_regex

try:
    from nltk.corpus import wordnet
except:
    nltk.download('wordnet')
    from nltk.corpus import wordnet

import string, re, pickle

import scipy
from scipy import spatial
from sklearn.ensemble import RandomForestClassifier

print("Importing and building WordSubstitution functionality, this might take a while the first time due to the dependencies...\nPlease be patient!")

############
###### embedding functionality - © Vishal
############
def getEmbeddings(filename):
    f = open(filename, encoding='utf-8')
    glove_embeddings = {}
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        glove_embeddings[word] = coefs
    f.close()
    return glove_embeddings


def wordVecLookup(word, embeddings):
    return embeddings.get(word)

def getSubstitutabilityVec(subWord, tarWord, context_items):
    vecSubWord = wordVecLookup(subWord, word_embeddings)
    vecTarWord = wordVecLookup(tarWord, word_embeddings)

    lstVecContextWords = []
    for token in context_items:
        ctxWordVec = wordVecLookup(token, context_embeddings)
        if ctxWordVec is not None:
            lstVecContextWords.append(ctxWordVec)

    return vecSubWord, vecTarWord, lstVecContextWords

def getSentenceDependents(sentence, target_word_index, nlp):
    """
    we need the nlp paramter here or else it does not work outside of this module. (inside this module nlp will be
    created in the main method below. (this does not work if you import the module)
    """
    doc = nlp(sentence)
    token = doc[target_word_index]

    sentence_dependencies = []
    relation_types_set = set()
    context_items = []

    if token != token.head:
        sentence_dependencies.append((token.head.text.lower(), token.head.lemma_, WordSubstitution.collapsePOSTag(token.head.tag_)))
        relation_types_set.add(token.dep_)
        context_items.append(token.dep_.lower() + 'I_' + token.head.text.lower())

    for element in doc:
        if element.head == token:
            sentence_dependencies.append((element.text.lower(), element.lemma_, WordSubstitution.collapsePOSTag(element.tag_)))
            relation_types_set.add(element.dep_)
            context_items.append(token.dep_.lower() + '_' + element.text.lower())

    relation_types = list(relation_types_set)
    return sentence_dependencies, relation_types, context_items

def add(subWord, tarWord, context_items):
    vecSubWord, vecTarWord, lstVecContextWords = getSubstitutabilityVec(subWord, tarWord, context_items)

    if vecSubWord is None or vecTarWord is None or len(lstVecContextWords) == 0:
        return -1
    
    val = scipy.spatial.distance.cosine(vecSubWord, vecTarWord)
    for vecContextWord in lstVecContextWords:
        val += scipy.spatial.distance.cosine(vecSubWord, vecContextWord)
        
    return val / (len(lstVecContextWords) + 1)

def balAdd(subWord, tarWord, context_items):
    vecSubWord, vecTarWord, lstVecContextWords = getSubstitutabilityVec(subWord, tarWord, context_items)

    if vecSubWord is None or vecTarWord is None or len(lstVecContextWords) == 0:
        return -1
    
    val = len(lstVecContextWords) * scipy.spatial.distance.cosine(vecSubWord, vecTarWord)
    for vecContextWord in lstVecContextWords:
        val += scipy.spatial.distance.cosine(vecSubWord, vecContextWord)
    
    return val / (2 * len(lstVecContextWords))

def mult(subWord, tarWord, context_items):
    vecSubWord, vecTarWord, lstVecContextWords = getSubstitutabilityVec(subWord, tarWord, context_items)

    if vecSubWord is None or vecTarWord is None or len(lstVecContextWords) == 0:
        return -1
    
    val = (scipy.spatial.distance.cosine(vecSubWord, vecTarWord) + 1)/2
    for vecContextWord in lstVecContextWords:
        val *= (scipy.spatial.distance.cosine(vecSubWord, vecContextWord) + 1)/2
    
    return val**(1/float((len(lstVecContextWords) + 1)))

def balMult(subWord, tarWord, context_items):
    vecSubWord, vecTarWord, lstVecContextWords = getSubstitutabilityVec(subWord, tarWord, context_items)

    if vecSubWord is None or vecTarWord is None or len(lstVecContextWords) == 0:
        return -1
    
    val = (scipy.spatial.distance.cosine(vecSubWord, vecTarWord) + 1)/2
    val = val**(len(lstVecContextWords))
    
    for vecContextWord in lstVecContextWords:
        val *= (scipy.spatial.distance.cosine(vecSubWord, vecContextWord) + 1)/2
    
    return val**(1/float((2 * len(lstVecContextWords))))

############
###### END read embedding functionality - © Vishal
############


############
###### Thesaurus functionality - © Vishal
############
def getThesaurusOnlineRelevance(targetLemPos):
    (lemma, spacy_tag) = targetLemPos
    all_synonyms = set()

    thesaurus_pos = ""
    if spacy_tag == 'JJ':
        thesaurus_pos = 'adj'
    if spacy_tag == 'VB':
        thesaurus_pos = 'verb'
    if spacy_tag == 'RB':
        thesaurus_pos = 'adv'
    if spacy_tag == 'NN':
        thesaurus_pos = 'noun'

    try:
        fp = urllib.request.urlopen('http://www.thesaurus.com/browse/'+lemma)
        html_bytes = fp.read()
        html_doc = html_bytes.decode('utf-8')
        fp.close()

        soup = BeautifulSoup(html_doc, 'html.parser')

        s1 = soup.find_all("script")[19].get_text()
        s1 = s1.replace('<script>', '')
        s1 = s1.replace('window.INITIAL_STATE = ', '')
        s1 = s1.replace(';</script>', '')
        s1 = s1[:-1]
        res = json.loads(s1)
        
        synBuckets = res['searchData']['relatedWordsApiData']['data']
        for elem in synBuckets:
            if elem['entry'] == lemma and elem['pos'] == thesaurus_pos:
                for syn in elem['synonyms']:
                    all_synonyms.add(syn['term'])

        all_synonyms = set(filter(remove_multiword,all_synonyms))
    except:
        all_synonyms = set()

    return all_synonyms

############
###### End Thesaurus functionality - © Vishal
############
word_embeddings = getEmbeddings("essay_evaluation/Corpora/lexsub_word_embeddings")
context_embeddings = getEmbeddings("essay_evaluation/Corpora/lexsub_context_embeddings")

class WordSubstitution(object):

    """
    Initializer
    args
    nlp: this should be a pipeline that contains the coref annotator
    """
    def __init__(self, nlp):
        punctnquotes = r'… …… , : ; \! \? ¿ ؟ ¡ \( \) \[ \] \{ \} < > _ # \* & 。 ？ ！ ， 、 ； ： ～ · । ، ؛ ٪\' \'\' " ” “ `` ` ‘ ´ ‘‘ ’’ ‚ , „ » « 「 」 『 』 （ ） 〔 〕 【 】 《 》 〈 〉'
        infix_re = re.compile(punctnquotes)
        prefix_re = compile_prefix_regex(nlp.Defaults.prefixes)
        suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)

        nlp.tokenizer = Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                                suffix_search=suffix_re.search,
                                infix_finditer=infix_re.finditer,
                                token_match=None)
                                
        self.nlp = nlp
        self.d = 1 #Wordnet distance
        self.estimators = 10
        self.crit = 'gini'
        self.max_f = 'auto'
        self.max_d = 1
        self.threshold = 0.3

        

        #set paths
        self.wordListCSVFile = 'essay_evaluation/Corpora/BritishWords_COCA_AmericanCounterparts.csv'
        self.fnameBritAmerWords = "essay_evaluation/Corpora/BritishWords_COCA_AmericanCounterparts.csv"
        self.word_embeddings_file = "essay_evaluation/Corpora/lexsub_word_embeddings"
        self.context_embeddings_file = "essay_evaluation/Corpora/lexsub_context_embeddings"
        self.fnameModel = "essay_evaluation/resources/subevalmodel"
    """
    Should get the text and return a new one with the words changed
    """
    def __call__(self, marked_sentence):
        return self.rank_synonyms(marked_sentence)

    @staticmethod
    def collapsePOSTag(tag):
        if tag in ['NN', 'NNS', 'NNP', 'NNPS']:
            return 'NN'
            
        elif tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
            return 'VB'
        
        elif tag in ['JJ', 'JJR', 'JJS']:
            return 'JJ'
        
        elif tag in ['RB', 'RBR', 'RBS', 'RP', 'WRB']:
            return 'RB'
        
        elif tag in ['DT', 'WDT', 'WP', 'PDT', 'PRP$', 'WP$']:
            return 'DT'
        
        else:
            return tag


    def getTargetLemPosIdx(self, sentence):
        doc = self.nlp(sentence)
        target_word_index = 0
        targetWord = ''
        for token in doc:
            if 'čš' in token.text: # Detect the special symbol ('čš') used to identify the target word
                targetWord = token.text.replace('čš', '')
                break
            target_word_index +=1

        #print(targetWord, target_word_index)

        # After  remove the special symbol from the sentence and tokenize again to get its correct POS Tag
        sentence = sentence.replace('čš', '')
        doc = self.nlp(sentence)
        tarWordPosition = 0
        targetLemma = ''
        targetSpecPosTag = ''
        for token in doc:
            if token.text in targetWord and tarWordPosition == target_word_index: # Detect the special symbol used to identify the target word
                targetWord = token.text
                targetLemma = token.lemma_
                targetSpecPosTag = token.tag_        
                break
            tarWordPosition +=1

        # Get the Gen Pos Tag for the Spec Pos Tag
        targetGenPosTag = self.collapsePOSTag(targetSpecPosTag)

        # Build the target word LemPos tuple
        targetLemPos = (targetLemma, targetGenPosTag)

        return targetWord, targetLemPos, target_word_index, sentence


    def getBritishAmericanWords(self):
        colNameBritish = 'British'
        colNameAmer = 'American'
        df = pd.read_csv(self.wordListCSVFile)
        
        brit = df[colNameBritish].tolist()
        amer = df[colNameAmer].tolist()
        
        wordList = list(zip(brit, amer))
        return wordList

    def mapBritToAmerWord(self, britWord):
        lstBritAmerWords = self.getBritishAmericanWords()
        for word in lstBritAmerWords:
            if word[0] == britWord:
                return word[1]
        return britWord


    def getWordnetDistance(self, targetLemPos, d=1):
        all_synonyms = set()
        (lemma, spacy_tag) = targetLemPos
        
        # We only need the synsets that have the same POS as the lemma
        wordnet_pos = ""
        if spacy_tag == 'JJ':
            wordnet_pos = wordnet.ADJ
        if spacy_tag == 'VB':
            wordnet_pos = wordnet.VERB
        if spacy_tag == 'RB':
            wordnet_pos = wordnet.ADV
        if spacy_tag == 'NN':
            wordnet_pos = wordnet.NOUN

        lemma_synsets = wordnet.synsets(lemma, wordnet_pos)

        for lemma_synset in lemma_synsets:
            all_synonyms = all_synonyms.union(set(lemma_synset.lemma_names()))

        hypo = lambda s: s.hyponyms()
        hyper = lambda s: s.hypernyms()
        similar = lambda s: s.similar_tos()
        distance = 1
        
        while distance < d:
            distance = distance + 1

            for lemma_synset in lemma_synsets:
                hyponyms = list(lemma_synset.closure(hypo, depth=distance))
                hypernyms = list(lemma_synset.closure(hyper, depth=distance))
                similar_tos = list(lemma_synset.closure(similar, depth=distance))

                for hyponym in hyponyms:
                    all_synonyms = all_synonyms.union(set(hyponym.lemma_names()))

                for hypernym in hypernyms:
                    all_synonyms = all_synonyms.union(set(hypernym.lemma_names()))

                for similar_to in similar_tos:
                    all_synonyms = all_synonyms.union(set(similar_to.lemma_names()))

        return all_synonyms
    
    def getWordnetCandidates(self, targetLemPos):
        all_synonyms = set()
        allTargetWords = set([targetLemPos[0], self.mapBritToAmerWord(targetLemPos[0])])
        for w in allTargetWords:
            s = self.getWordnetDistance((w, targetLemPos[1]), self.d)
            for w in s:
                all_synonyms.add(w)
        return all_synonyms

    def remove_multiword(self, item):
        if ' ' in item or '_' in item:
            return False
        return True
    
    def getThesaurusCandidates(self, targetLemPos):
        all_synonyms = set()
        allTargetWords = set([targetLemPos[0], self.mapBritToAmerWord(targetLemPos[0])])
        for w in allTargetWords:
            s = getThesaurusOnlineRelevance((w, targetLemPos[1]))
            for w in s:
                all_synonyms.add(w)
        return all_synonyms

    def getSynonynms(self, targetLemPos):   
        # Fetch the Wordnet candidates
        wordnetCandidates = self.getWordnetCandidates(targetLemPos)
        
        # Fetch the Thesaurus candidates
        thesaurusCandidates = self.getThesaurusCandidates(targetLemPos)
        
        allSynonyms = wordnetCandidates.union(thesaurusCandidates)
        
        return allSynonyms
    
    def rank_synonyms(self, marked_sentence):
        targetWord, targetLemPos, target_word_index, sentence = self.getTargetLemPosIdx(marked_sentence)
        allSynonyms = self.getSynonynms(targetLemPos)

        allSynonyms = set([self.mapBritToAmerWord(s) for s in allSynonyms])

        xTestInfo = []
        xTestFeat5_8 = []
        # print('Getting context items ... ')
        sentence_dependencies, relation_types, context_items = getSentenceDependents(sentence, target_word_index, self.nlp)

        lemma = targetLemPos[0]
        for synonym in allSynonyms:
            valAdd = add(synonym, lemma, context_items)
            valBalAdd = balAdd(synonym, lemma, context_items)
            valMult = mult(synonym, lemma, context_items)
            valBalMult = balMult(synonym, lemma, context_items)

            xTestInfo.append([lemma, synonym, sentence])
            xTestFeat5_8.append([valAdd, valBalAdd, valMult, valBalMult])

        with open (self.fnameModel, 'rb') as fp:
            modelRF = pickle.load(fp)
        yPredProba = modelRF.predict_proba(xTestFeat5_8)[:,1]

        candidates = zip(xTestInfo, yPredProba)
        synonymPredOp = []
        for x in candidates:
            synonymPredOp.append((x[0][1], x[1]))

        # Sort by descending
        synonymsRankedPred = sorted(synonymPredOp, key=lambda x: x[1], reverse=True)

        synonymsRankedClass = []
        # Use threshold to decide the label
        for tup in synonymsRankedPred:
            if tup[1] >= self.threshold: # label = 1        
                synonymsRankedClass.append(tup[0])

        dictSynonyms = { "targetlemma" : targetLemPos[0],
                    "targetPOSTag" : targetLemPos[1],
                    "rankedSynonyms" : [x for x in synonymsRankedClass]
                }
        
        return dictSynonyms


if __name__ == "__main__":
    nlp = spacy.load("en_core_web_sm")
    ws = WordSubstitution(nlp)
    print(ws("The public were deeply čšscepticalčš about some of the proposals."))