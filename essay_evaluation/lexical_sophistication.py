import os

import pandas as pd
import pyphen
import spacy
from spacy.tokens.doc import Doc

from essay_evaluation import FeaturePipelineComponent

features_ls = ["LS_FPC_NG", "LS_FPC_NA", "LS_FPC_TC", "LS_FPC_BS", "LS_FPC_CA", "LS_FPC_CT", "LS_FPC_CGA1",
               "LS_FPC_CGA2", "LS_FPC_CGA3", "LS_FOMN_NG", "LS_FOMN_NA", "LS_FOMN_TC", "LS_FOMN_BS", "LS_FOMN_CA",
               "LD_AVG_CH", "LD_NUM_SYLL"]


##Lexical Density features implemented on the lexical sophistication class due to use of the same files,
## and for the main reason to avoid reading the same files again
##TODO: Implement here as well in case we want just the LD features.
class LexicalSophisticationFeatures(FeaturePipelineComponent):
    name = "features_ls"

    feature_names = ["LS_FPC_NG", "LS_FPC_NA", "LS_FPC_TC", "LS_FPC_BS", "LS_FPC_CA", "LS_FPC_CT", "LS_FPC_CGA1",
                   "LS_FPC_CGA2", "LS_FPC_CGA3", "LS_FOMN_NG", "LS_FOMN_NA", "LS_FOMN_TC", "LS_FOMN_BS", "LS_FOMN_CA",
                   #"LD_AVG_CH", "LD_NUM_SYLL"
                    ]

    ##Create phase
    def __init__(self, paths=None):
        """
        paths:list -> a list of string, each of which represents a path to one of the corpora needed as listed below.
        This method initialized constant accross the object to be used by other methods of this object
        """

        super().__init__()
        if not Doc.has_extension(self.name):
            Doc.set_extension(self.name, default=[])
            Doc.set_extension('ngsl_words', default=[])
            Doc.set_extension('nawl_words', default=[])
            Doc.set_extension('tsl_words', default=[])
            Doc.set_extension('fpc_words', default=[])
            Doc.set_extension('cocaacad_words', default=[])
            Doc.set_extension('cocatech_words', default=[])
            Doc.set_extension('cocagenband1_words', default=[])
            Doc.set_extension('cocagenband2_words', default=[])
            Doc.set_extension('cocagenband3_words', default=[])

        if paths is None:
            #file locations
            self.fnameNGSL = os.path.join(os.path.dirname(__file__), 'Corpora/NGSL+1.01+by+band - Frequency.csv')
            self.fnameNAWL = os.path.join(os.path.dirname(__file__), 'Corpora/NAWL_SFI.csv')
            self.fnameBSL = os.path.join(os.path.dirname(__file__), 'Corpora/BSL_1.01_SFI_freq_bands.csv')
            self.fnameTSL = os.path.join(os.path.dirname(__file__), 'Corpora/TSL+1.1+Ranked+by+Frequency - TSL.csv')
            self.fnameCOCAAcad = os.path.join(os.path.dirname(__file__), 'Corpora/COCA Academic.csv')
            self.fnameCOCATech = os.path.join(os.path.dirname(__file__), 'Corpora/COCA Technical.csv')
            self.fnameCOCAGen = os.path.join(os.path.dirname(__file__), 'Corpora/COCA General.csv')
        else:
            #file locations passed as a parameter to the construct
            self.fnameNGSL = paths[0]
            self.fnameNAWL = paths[1]
            self.fnameBSL = paths[2]
            self.fnameTSL = paths[3]
            self.fnameCOCAAcad = paths[4]
            self.fnameCOCATech = paths[5]
            self.fnameCOCAGen = paths[6]

        ## Taken by Vishal's code.
        self.NGSLTotal = 273613534
        self.NAWLTotal = 288176225
        self.TSLTotal = 1560194
        self.BSLTotal = 64651722
        self.COCAAcadTotal = 120032441

        # read the corpora
        self.read_corpora()
        self.nlp = spacy.load("en_core_web_sm")

    def __call__(self, doc):
        """
        doc: Doc -> spacy pipeline will pass a doc with all the attributes for each document
        return: Doc -> same doc object to whom we've just added the lexical sophistication features
        """
        features_ls = self.get_ls_ld_features(doc)

        # TODO: @Aldi: Please check if the mapping is correct. I used the feature_names array as reference.
        doc._.features['LS_FPC_NG'] = features_ls[0]
        doc._.features['LS_FPC_NA'] = features_ls[1]
        doc._.features['LS_FPC_TC'] = features_ls[2]
        doc._.features['LS_FPC_BS'] = features_ls[3]
        doc._.features['LS_FPC_CA'] = features_ls[4]
        doc._.features['LS_FPC_CT'] = features_ls[5]
        doc._.features['LS_FPC_CGA1'] = features_ls[6]
        doc._.features['LS_FPC_CGA2'] = features_ls[7]
        doc._.features['LS_FPC_CGA3'] = features_ls[8]
        doc._.features['LS_FOMN_NG'] = features_ls[9]
        doc._.features['LS_FOMN_NA'] = features_ls[10]
        doc._.features['LS_FOMN_TC'] = features_ls[11]
        doc._.features['LS_FOMN_BS'] = features_ls[12]
        doc._.features['LS_FOMN_CA'] = features_ls[13]

        # deprecated! use doc._.features instead
        doc._.features_ls = features_ls

        return doc

    # read data and store it in the object
    def read_corpora(self):
        """
        Read the corporas from the paths saved on the init, and save them on the constant of the object.
        """

        self.lstNGSL = self.get_NGSL()
        self.lstNAWL = self.get_NAWL()
        self.lstTSL = self.get_TSL()
        self.lstBSL = self.get_BSL()
        self.lstCOCAAcadLemPos, self.lstCOCAAcadLemPosFreq = self.get_COCAAcad()
        self.lstCOCATechLemPos, self.lstCOCATechLemPosFreq = self.get_COCATech()
        self.lstCOCAGenLemPos, self.lstCOCAGenLemPosFreq = self.get_COCAGen()

    def get_sent_from_text(self, txtSent):
        """
        txtSent: string -> a text represented as a string
        return: list -> returns a list that contains strings for
        """
        lstSent = []
        doc = self.nlp(txtSent)
        for sent in doc.sents:
            lstSent.append(sent.text)
        return lstSent

    # TODO: If provided from Alejandro this needs to be removed because text is already lemmatized and POS tagged.
    def get_lemmatized_pos_tagged_sent(self, lstSent):
        lstLemPOSWords = []

        for doc in lstSent:
            doc = self.nlp(doc)
            for token in doc:
                l = ''
                if token.lemma_ == '-PRON-':
                    l = token.text
                else:
                    l = token.lemma_

                lstLemPOSWords.append((l.lower(), token.tag_))

        return lstLemPOSWords

    def get_words_from_text(self, lstSent):
        lstWords = []
        for doc in lstSent:
            doc = self.nlp(doc)
            for token in doc:
                l = ''
                if token.lemma_ == '-PRON-':
                    l = token.text
                else:
                    l = token.lemma_

                lstWords.append(l.lower())

        return lstWords

    def get_NGSL(self):
        colNameWord = 'Lemma'
        df = pd.read_csv(self.fnameNGSL)
        lstNSGL = df[colNameWord].tolist()
        return lstNSGL

    def get_NAWL(self):
        colNameWord = 'Word'
        df = pd.read_csv(self.fnameNAWL)
        lstNAWL = df[colNameWord].tolist()
        return lstNAWL

    ### TOEIC Service List
    def get_TSL(self):
        colNameWord = 'Word'
        df = pd.read_csv(self.fnameTSL)
        lstTSL = df[colNameWord].tolist()
        return lstTSL

    ### Business Service List
    def get_BSL(self):
        colNameWord = 'Word'
        df = pd.read_csv(self.fnameBSL)
        lstBSL = df[colNameWord].tolist()
        return lstBSL

    ### COCA Academic List
    def get_COCAAcad(self):
        colNameWord = 'word'
        colNamePOS = 'SpaCy tag'
        df = pd.read_csv(self.fnameCOCAAcad)
        lstCOCAAcadWord = df[colNameWord].tolist()
        lstCOCAAcadPos = df[colNamePOS].tolist()
        lstCOCAAcadLemPos = list(zip(lstCOCAAcadWord, lstCOCAAcadPos))

        colCOCAAcadFreq = 'COCA-Acad'
        lstCOCAAcadFreq = df[colCOCAAcadFreq].tolist()
        lstCOCAAcadLemPosFreq = list(zip(lstCOCAAcadWord, lstCOCAAcadPos, lstCOCAAcadFreq))

        return lstCOCAAcadLemPos, lstCOCAAcadLemPosFreq

    ### COCA Academic Technical List
    def get_COCATech(self):
        colNameWord = 'word'
        colNamePOS = 'SpaCy tag'
        df = pd.read_csv(self.fnameCOCATech)
        lstCOCATechWord = df[colNameWord].tolist()
        lstCOCATechPos = df[colNamePOS].tolist()
        lstCOCATechLemPos = list(zip(lstCOCATechWord, lstCOCATechPos))

        colCOCATechFreq = 'COCA-Acad'
        lstCOCATechFreq = df[colCOCATechFreq].tolist()
        lstCOCATechLemPosFreq = list(zip(lstCOCATechWord, lstCOCATechPos, lstCOCATechFreq))

        return lstCOCATechLemPos, lstCOCATechLemPosFreq

    ### COCA Academic General List
    def get_COCAGen(self):
        colNameWord = 'word'
        colNamePOS = 'SpaCy tag'
        df = pd.read_csv(self.fnameCOCAGen)
        lstCOCAGenWord = df[colNameWord].tolist()
        lstCOCAGenPos = df[colNamePOS].tolist()
        lstCOCAGenLemPos = list(zip(lstCOCAGenWord, lstCOCAGenPos))

        colCOCAGenFreq = 'COCA-Acad'
        lstCOCAGenFreq = df[colCOCAGenFreq].tolist()
        lstCOCAGenLemPosFreq = list(zip(lstCOCAGenWord, lstCOCAGenPos, lstCOCAGenFreq))
        return lstCOCAGenLemPos, lstCOCAGenLemPosFreq

    def get_prop_NGSLWords(self, lstWords, doc):
        lstIntersect = list(set(lstWords) & set(self.lstNGSL))
        doc._.ngsl_words = lstIntersect
        propWordsNGSL = len(lstIntersect) / len(lstWords)
        return propWordsNGSL

    # Code: LS_FPC_NA
    def get_prop_NAWLWords(self, lstWords, doc):
        lstIntersect = list(set(lstWords) & set(self.lstNAWL))
        doc._.nawl_words = lstIntersect
        propWordsNAWL = len(lstIntersect) / len(lstWords)
        return propWordsNAWL

    # Code: LS_FPC_TC
    def get_prop_TSLWords(self, lstWords, doc):
        lstIntersect = list(set(lstWords) & set(self.lstTSL))
        doc._.tsl_words = lstIntersect
        propWordsTSL = len(lstIntersect) / len(lstWords)
        return propWordsTSL

    # Code: LS_FPC_BS
    def get_prop_BSLWords(self, lstWords, doc):
        lstIntersect = list(set(lstWords) & set(self.lstBSL))
        doc._.fpc_words = lstIntersect
        propWordsBSL = len(lstIntersect) / len(lstWords)
        return propWordsBSL

    # Code: LS_FPC_CA
    def get_prop_COCAAcadWords(self, lstLemPOSWords, doc):
        lstIntersect = list(set(lstLemPOSWords) & set(self.lstCOCAAcadLemPos))
        doc._.cocaacad_words = lstIntersect
        propWordsCOCAAcad = len(lstIntersect) / len(lstLemPOSWords)
        return propWordsCOCAAcad

    # Code: LS_FPC_CT
    def get_prop_COCATechWords(self, lstLemPOSWords, doc):
        lstIntersect = list(set(lstLemPOSWords) & set(self.lstCOCATechLemPos))
        doc._.cocatech_words = lstIntersect
        propWordsCOCATech = len(lstIntersect) / len(lstLemPOSWords)
        return propWordsCOCATech

    # Code: LS_FPC_CGA1
    def get_prop_COCAGenBand1(self, lstLemPOSWords, doc):
        lstIntersect = list(set(lstLemPOSWords) & set(self.lstCOCAGenLemPos[0:3000]))
        doc._.cocagenband1_words = lstIntersect
        propWordsCOCAGenBand1 = len(lstIntersect) / len(lstLemPOSWords)
        return propWordsCOCAGenBand1

    # Code: LS_FPC_CGA2
    def get_prop_COCAGenBand2(self, lstLemPOSWords, doc):
        lstIntersect = list(set(lstLemPOSWords) & set(self.lstCOCAGenLemPos[3000:6000]))
        doc._.cocagenband2_words = lstIntersect
        propWordsCOCAGenBand2 = len(lstIntersect) / len(lstLemPOSWords)
        return propWordsCOCAGenBand2

    # Code: LS_FPC_CGA3
    def get_prop_COCAGenBand3(self, lstLemPOSWords, doc):
        lstIntersect = list(set(lstLemPOSWords) & set(self.lstCOCAGenLemPos[6000:9000]))
        doc._.cocagenband3_words = lstIntersect
        propWordsCOCAGenBand3 = len(lstIntersect) / len(lstLemPOSWords)
        return propWordsCOCAGenBand3

    def get_mean_freq_COCAAcadWords(self, lstLemPOSWords):
        lstIntersect = list(set(lstLemPOSWords) & set(self.lstCOCAAcadLemPos))
        sumFreq = 0
        for word in lstIntersect:
            for lwf in self.lstCOCAAcadLemPosFreq:
                if word[0] == lwf[0] and word[1] == lwf[1]:  # checking the word and the POS tag
                    sumFreq += float(lwf[2].replace(',', ''))  # add the frequency of this word

        if len(lstIntersect) == 0:
            meanFreqWordsCOCAAcad = 0
        else:
            meanFreqWordsCOCAAcad = sumFreq / len(lstIntersect)
        return meanFreqWordsCOCAAcad

    # Code: LS_FOMN_CT
    def get_mean_freq_COCATechWords(self, lstLemPOSWords):
        lstIntersect = list(set(lstLemPOSWords) & set(self.lstCOCATechLemPos))
        sumFreq = 0
        for word in lstIntersect:
            for lwf in self.lstCOCATechLemPosFreq:
                if word[0] == lwf[0] and word[1] == lwf[1]:
                    sumFreq += float(lwf[2].replace(',', ''))
        if len(lstIntersect) == 0:
            meanFreqWordsCOCATech = 0
        else:
            meanFreqWordsCOCATech = sumFreq / len(lstIntersect)
        return meanFreqWordsCOCATech

    # Code: LS_FOMN_CGA1
    def get_mean_freq_COCAGenBand1(self, lstLemPOSWords):
        lstIntersect = list(set(lstLemPOSWords) & set(self.lstCOCAGenLemPos[0:3000]))
        sumFreq = 0
        for word in lstIntersect:
            for lwf in self.lstCOCAGenLemPosFreq[0:3000]:
                if word[0] == lwf[0] and word[1] == lwf[1]:
                    sumFreq += float(lwf[2].replace(',', ''))

        if len(lstIntersect) == 0:
            meanFreqWordsCOCAGenBand1 = 0
        else:
            meanFreqWordsCOCAGenBand1 = sumFreq / len(lstIntersect)
        return meanFreqWordsCOCAGenBand1

    # Code: LS_FOMN_CGA2
    def get_mean_freq_COCAGenBand2(self, lstLemPOSWords):
        lstIntersect = list(set(lstLemPOSWords) & set(self.lstCOCAGenLemPos[3000:6000]))
        sumFreq = 0
        for word in lstIntersect:
            for lwf in self.lstCOCAGenLemPosFreq[3000:6000]:
                if word[0] == lwf[0] and word[1] == lwf[1]:
                    sumFreq += float(lwf[2].replace(',', ''))

        if len(lstIntersect) == 0:
            meanFreqWordsCOCAGenBand2 = 0
        else:
            meanFreqWordsCOCAGenBand2 = sumFreq / len(lstIntersect)
        return meanFreqWordsCOCAGenBand2

    # Code: LS_FOMN_CGA3
    def get_mean_freq_COCAGenBand3(self, lstLemPOSWords):
        lstIntersect = list(set(lstLemPOSWords) & set(self.lstCOCAGenLemPos[6000:9000]))
        sumFreq = 0
        for word in lstIntersect:
            for lwf in self.lstCOCAGenLemPosFreq[6000:9000]:
                if word[0] == lwf[0] and word[1] == lwf[1]:
                    sumFreq += float(lwf[2].replace(',', ''))

        if len(lstIntersect) == 0:
            meanFreqWordsCOCAGenBand3 = 0
        else:
            meanFreqWordsCOCAGenBand3 = sumFreq / len(lstIntersect)
        return meanFreqWordsCOCAGenBand3

    def lex_sophistication_density_features(self, doc, lstWords, lstLemPOSWords):
        lstLexSopFeats = []

        lstLexDenFeats = []

        lstLexSopFeats.append(self.get_prop_NGSLWords(lstWords, doc))
        lstLexSopFeats.append(self.get_prop_NAWLWords(lstWords, doc))
        lstLexSopFeats.append(self.get_prop_TSLWords(lstWords, doc))
        lstLexSopFeats.append(self.get_prop_BSLWords(lstWords, doc))
        lstLexSopFeats.append(self.get_prop_COCAAcadWords(lstLemPOSWords, doc))
        lstLexSopFeats.append(self.get_prop_COCATechWords(lstLemPOSWords, doc))
        lstLexSopFeats.append(self.get_prop_COCAGenBand1(lstLemPOSWords, doc))
        lstLexSopFeats.append(self.get_prop_COCAGenBand2(lstLemPOSWords, doc))
        lstLexSopFeats.append(self.get_prop_COCAGenBand3(lstLemPOSWords, doc))

        lstLexSopFeats.append(self.get_mean_freq_COCAAcadWords(lstLemPOSWords))
        lstLexSopFeats.append(self.get_mean_freq_COCATechWords(lstLemPOSWords))
        lstLexSopFeats.append(self.get_mean_freq_COCAGenBand1(lstLemPOSWords))
        lstLexSopFeats.append(self.get_mean_freq_COCAGenBand2(lstLemPOSWords))
        lstLexSopFeats.append(self.get_mean_freq_COCAGenBand3(lstLemPOSWords))

        # These are not lexical density features - check code below class: LexicalDensityFeatures
        # lstLexDenFeats = self.get_lex_density_features(lstWords)

        return lstLexSopFeats

    def get_ls_ld_features(self, doc):
        txtSample = doc.text

        lstSent = self.get_sent_from_text(txtSample)
        lstWords = self.get_words_from_text(lstSent)
        lstLemPOSWords = self.get_lemmatized_pos_tagged_sent(lstSent)

        # lstLexDenFeats = lexDenFeats(lstSent, lstWords, lstLemPOSWords)
        lstLexSopDenFeats = self.lex_sophistication_density_features(doc, lstWords, lstLemPOSWords)

        # lstLexicalFeatures = lstLexDenFeats + lstLexSopFeats
        lstLexicalFeatures = lstLexSopDenFeats

        return lstLexicalFeatures

    # Lexical Density Features in the same class since they use the same corpora
    # and it would be smart not to read twice the same thing.

    ##TODO: The lexical density features apperantly have a little bit more work than I
    #       previously anticipated, so I will work on them at a later point in time.

    def avg_num_char(self, lstWords):
        sumChar = 0
        for word in lstWords:
            ch = len(list(word))
            sumChar += ch

        numChar = sumChar / len(lstWords)
        return numChar

    def num_syll(self, lstWords):

        dic = pyphen.Pyphen(lang="en")

        sumSyll = 0
        for word in lstWords:
            ch = len(list(word))
            hyphenatedWord = dic.inserted(word)
            syll = len(hyphenatedWord.split('-'))
            sumSyll += syll

        numSyll = sumSyll / len(lstWords)
        return numSyll

    def get_lex_density_features(self, lstWords):
        lexDensFeatures = []

        numChar = self.avg_num_char(lstWords)
        numSyll = self.num_syll(lstWords)

        lexDensFeatures.append(numChar)
        lexDensFeatures.append(numSyll)

        return lexDensFeatures
